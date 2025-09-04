import sqlite3


class Database:
    def __init__(self, db_path: str = "db.db"):
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        _cursor = self._connection.cursor()
        _cursor.execute("""
            CREATE TABLE IF NOT EXISTS clones (
                pid INTEGER PRIMARY KEY,
                exe_path TEXT NOT NULL
            )
        """)
        self._connection.commit()

    def drop_tables(self):
        _cursor = self._connection.cursor()
        _cursor.execute("DROP TABLE IF EXISTS clones")
        self._connection.commit()
