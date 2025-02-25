# filepath: /C:/Users/Zack/Desktop/School stuff/Sheet_Metal_Project/sheet_metal_scraper/scraper/scrapy_project/items.py

import scrapy

class TenderItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    date = scrapy.Field()
    open_date = scrapy.Field()
    close_date = scrapy.Field()
    link = scrapy.Field()