import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def create_connection():
    """Create and return a connection to the PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL)

def create_tables():
    """Create the tenders table if it doesn't already exist."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenders (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            date_posted DATE,
            closing_date DATE,
            link TEXT,
            status TEXT DEFAULT 'New'
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def insert_tender(title, description, date_posted, closing_date, link, status="New"):
    """Insert a new tender into the tenders table."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tenders (title, description, date_posted, closing_date, link, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (title, description, date_posted, closing_date, link, status))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
