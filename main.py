import argparse
from src.database import Database
from src.system import System

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, help="PID of the process to clone")
    parser.add_argument("--count", type=int, default=1, help="Number of clones")
    parser.add_argument("--remove", action="store_true", help="Remove all clones")
    parser.add_argument("--father_pid", type=int, help="Simulated parent PID for clones")

    args = parser.parse_args()
    db = Database()
    system = System(db)

    if args.remove:
        system.remove_clones()
        return

    if not args.pid:
        print("Please specify --pid")
        return

    system.clone_process(pid=args.pid, count=args.count, father_pid=args.father_pid)

if __name__ == "__main__":
    main()
