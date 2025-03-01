# pipelines.py
import sqlite3

class TenderPipeline:
    def open_spider(self, spider):
        self.conn = sqlite3.connect('tenders.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tenders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                date_posted TEXT,
                open_date TEXT,
                closing_date TEXT,
                link TEXT,
                status TEXT DEFAULT 'New'
            )
        ''')

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        self.cursor.execute('''
            INSERT INTO tenders (title, description, date_posted, open_date, closing_date, link, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['title'], 
            item['description'], 
            item.get('date_posted', item.get('date')), 
            item.get('open_date', ""), 
            item.get('closing_date', item.get('close_date', "")), 
            item['link'],
            "New"
        ))
        return item
