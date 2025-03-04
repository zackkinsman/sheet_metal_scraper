CREATE TABLE IF NOT EXISTS tenders (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    date_posted DATE, 
    closing_date DATE,
    link TEXT,
    status TEXT DEFAULT 'New'
);
