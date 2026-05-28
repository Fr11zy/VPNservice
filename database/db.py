import sqlite3
from threading import Lock

class Database:
    def __init__(self, path):
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.connection.row_factory = sqlite3.Row
        self.cursor = None
        self.lock = Lock()

    def __del__(self):
        self.connection.close()

    def create_database(self, schema: dict):
        req = ""
        self.cursor = self.connection.cursor()
        for item in schema['database']['tables']:
            table_name, table_def = next(iter(item.items()))
            fields = table_def["fields"]
            cols = []
            for f in fields:
                col_name, col_def = next(iter(f.items()))
                cols.append(f'"{col_name}" {col_def}')
            req = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(cols)});'
            self.cursor.execute(req)
            
        self.connection.commit()

    def execute(self, query, params=()):
        with self.lock:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        
    def fetchone(self, query, params=()):
        with self.lock:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        
    def fetchall(self, query, params=()):
        with self.lock:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()