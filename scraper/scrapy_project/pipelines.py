# filepath: /C:/Users/Zack/Desktop/School stuff/Sheet_Metal_Project/sheet_metal_scraper/scraper/scrapy_project/pipelines.py

import sqlite3

class TenderPipeline:
    def open_spider(self, spider):
        self.conn = sqlite3.connect('tenders.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tenders (
                id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT,
                date TEXT,
                open_date TEXT,
                close_date TEXT,
                link TEXT
            )
        ''')

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        self.cursor.execute('''
            INSERT INTO tenders (title, description, date, open_date, close_date, link) VALUES (?, ?, ?, ?, ?, ?)
        ''', (item['title'], item['description'], item['date'], item['open_date'], item['close_date'], item['link']))
        return item