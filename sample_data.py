from db.database import create_tables, insert_tender

class SampleDataInserter:
    def __init__(self):
        self.insert_sample_data()

    def insert_sample_data(self):
        # Ensure the table exists using the updated schema.
        sample_tenders = [
            {
                "title": "Tender 1: Bridge Construction",
                "description": "Construction of a new downtown bridge.",
                "date_posted": "2025-01-15",
                "open_date": "2025-01-20",
                "closing_date": "2025-02-15",
                "link": "http://example.com/tender1",
                "status": "New"
            },
            {
                "title": "Tender 2: Road Repair",
                "description": "Repairs for the main highway following storm damage.",
                "date_posted": "2025-01-10",
                "open_date": "2025-01-12",
                "closing_date": "2025-02-10",
                "link": "http://example.com/tender2",
                "status": "New"
            },
            {
                "title": "Tender 3: Office Renovation",
                "description": "Renovation of corporate headquarters office space.",
                "date_posted": "2025-02-01",
                "open_date": "2025-02-05",
                "closing_date": "2025-03-01",
                "link": "http://example.com/tender3",
                "status": "New"
            }
        ]

        for tender in sample_tenders:
            insert_tender(
                tender["title"],
                tender["description"],
                tender["date_posted"],
                tender["open_date"],
                tender["closing_date"],
                tender["link"],
                tender["status"]
            )
        print("Sample tenders inserted.")

if __name__ == "__main__":
    SampleDataInserter()
