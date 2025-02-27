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
            title TEXT NOT NULL,
            description TEXT,
            date_posted TEXT,
            open_date TEXT,
            closing_date TEXT,
            link TEXT,
            status TEXT DEFAULT 'New'
        )
    """)
    conn.commit()
    conn.close()

def insert_tender(title, description, date_posted, open_date, closing_date, link, status="New"):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tenders (title, description, date_posted, open_date, closing_date, link, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, description, date_posted, open_date, closing_date, link, status))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
