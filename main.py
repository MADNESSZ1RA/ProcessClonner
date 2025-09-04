from src.database import Database
from src.system import System

db = Database()
system = System(db, 
                # programm_name="v2RayTun.exe",
                pid=15432
                )

if __name__ == "__main__":
    system.clone_suspended_process(10)
    # system.remove_all_clones()