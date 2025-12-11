import sqlite3
import os

DB_PATH = 'db.sqlite3'

def inspect_db():
    if not os.path.exists(DB_PATH):
        print(f"Database file {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"--- Database: {DB_PATH} ---")
    print(f"Found {len(tables)} tables:")

    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT count(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"- {table_name}: {count} rows")
        
        # Optional: Print columns for each table
        # cursor.execute(f"PRAGMA table_info({table_name})")
        # columns = [info[1] for info in cursor.fetchall()]
        # print(f"  Columns: {', '.join(columns)}")

    conn.close()

if __name__ == "__main__":
    inspect_db()
