import os
import psutil
import ctypes
from ctypes import wintypes
from src.database import Database

CREATE_SUSPENDED = 0x4
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

class STARTUPINFO(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD),
                ('lpReserved', wintypes.LPWSTR),
                ('lpDesktop', wintypes.LPWSTR),
                ('lpTitle', wintypes.LPWSTR),
                ('dwX', wintypes.DWORD),
                ('dwY', wintypes.DWORD),
                ('dwXSize', wintypes.DWORD),
                ('dwYSize', wintypes.DWORD),
                ('dwXCountChars', wintypes.DWORD),
                ('dwYCountChars', wintypes.DWORD),
                ('dwFillAttribute', wintypes.DWORD),
                ('dwFlags', wintypes.DWORD),
                ('wShowWindow', wintypes.WORD),
                ('cbReserved2', wintypes.WORD),
                ('lpReserved2', ctypes.POINTER(ctypes.c_byte)),
                ('hStdInput', wintypes.HANDLE),
                ('hStdOutput', wintypes.HANDLE),
                ('hStdError', wintypes.HANDLE)]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [('hProcess', wintypes.HANDLE),
                ('hThread', wintypes.HANDLE),
                ('dwProcessId', wintypes.DWORD),
                ('dwThreadId', wintypes.DWORD)]

class System:
    def __init__(self, db: Database, programm_name: str = None, pid: int = None):
        if not programm_name and not pid:
            raise ValueError("You must provide either programm_name or pid")
        self._programm_name = programm_name
        self._pid = pid
        self.db = db

    def _check_processes(self):
        processes = []
        for process in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                processes.append(process.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes

    def clone_suspended_process(self, count: int = 1):
        targets = []

        if self._pid:
            for proc in self._check_processes():
                if proc['pid'] == self._pid:
                    targets.append(proc)
                    break
        elif self._programm_name:
            targets = [proc for proc in self._check_processes() if proc['name'] == self._programm_name]

        if not targets:
            print("No target processes found.")
            return

        for process in targets:
            exe_path = process.get("exe")
            if exe_path and os.path.exists(exe_path):
                for i in range(count):
                    si = STARTUPINFO()
                    si.cb = ctypes.sizeof(si)
                    pi = PROCESS_INFORMATION()

                    success = kernel32.CreateProcessW(
                        ctypes.c_wchar_p(exe_path),
                        None,
                        None,
                        None,
                        False,
                        CREATE_SUSPENDED,
                        None,
                        None,
                        ctypes.byref(si),
                        ctypes.byref(pi)
                    )

                    if success:
                        print(f"Started suspended clone {i+1}/{count}: PID {pi.dwProcessId}")
                        _cursor = self.db._connection.cursor()
                        _cursor.execute(
                            "INSERT OR REPLACE INTO clones (pid, exe_path) VALUES (?, ?)",
                            (pi.dwProcessId, exe_path)
                        )
                        self.db._connection.commit()
                    else:
                        print(f"Failed to create suspended clone {i+1}")

    def remove_all_clones(self):
        _cursor = self.db._connection.cursor()
        _cursor.execute("SELECT pid, exe_path FROM clones")
        clones = _cursor.fetchall()

        for pid, exe_path in clones:
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=3)
                print(f"Terminated clone PID {pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"Could not terminate PID {pid}")

        _cursor.execute("DELETE FROM clones")
        self.db._connection.commit()
        print("All clones removed.")
