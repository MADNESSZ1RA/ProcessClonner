import subprocess
from .database import Database
import psutil

class System:
    def __init__(self, db: Database):
        self.db = db

    def clone_process(self, pid: int, count: int = 1, father_pid: int = 0):
        args = ["src/process_clone.exe", str(pid), str(father_pid), str(count)]
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stderr)
            return

        for line in result.stdout.splitlines():
            clone_pid = int(line.strip())
            self.db.add_clone(original_pid=pid, clone_pid=clone_pid)
            print(f"New clone PID: {clone_pid}")

    def remove_clones(self):
        clones = self.db.get_clones()
        for _, _, clone_pid in clones:
            try:
                proc = psutil.Process(clone_pid)
                proc.terminate()
            except psutil.NoSuchProcess:
                pass
        self.db.remove_all_clones()
        print("All clones removed")
