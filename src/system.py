import subprocess
from typing import Optional
from .database import Database
import psutil

class System:
    def __init__(self, db: Database):
        self.db = db

    def clone_process(self, pid: int, count: int = 1, father_pid: Optional[int] = None):
        args = ["process_clone.exe", str(pid), str(count)]
        if father_pid:
            args.append(str(father_pid))  # <-- передаём в C++ для симуляции родителя

        try:
            result = subprocess.run(args, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return

            for line in result.stdout.splitlines():
                clone_pid = int(line.strip())
                self.db.add_clone(original_pid=pid, clone_pid=clone_pid)
                print(f"New clone PID: {clone_pid}")
        except Exception as e:
            print(f"Failed to run process_clone.exe: {e}")

    def remove_clones(self):
        clones = self.db.get_clones()
        for _, _, clone_pid in clones:
            try:
                proc = psutil.Process(clone_pid)
                proc.terminate()
                print(f"Terminated clone PID {clone_pid}")
            except psutil.NoSuchProcess:
                pass
        self.db.remove_all_clones()
        print("All clones removed from DB and system")
