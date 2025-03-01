CREATE TABLE IF NOT EXISTS tenders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    date_posted TEXT,
    open_date TEXT,
    closing_date TEXT,
    link TEXT,
    status TEXT DEFAULT 'New'
);
