import sqlite3
from typing import List, Optional

class Database:
    def __init__(self, db_path: str = "db.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_pid INTEGER,
            clone_pid INTEGER
        )
        """)
        self.conn.commit()

    def add_clone(self, original_pid: int, clone_pid: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO clones (original_pid, clone_pid) VALUES (?, ?)",
            (original_pid, clone_pid)
        )
        self.conn.commit()

    def get_clones(self) -> List[tuple]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, original_pid, clone_pid FROM clones")
        return cursor.fetchall()

    def remove_all_clones(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM clones")
        self.conn.commit()
