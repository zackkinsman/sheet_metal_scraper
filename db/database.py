import sqlite3

DB_NAME = "tenders.db"

def create_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            deadline TEXT,
            link TEXT
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
