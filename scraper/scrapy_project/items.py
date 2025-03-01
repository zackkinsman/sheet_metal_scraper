# items.py
import scrapy

class TenderItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    date_posted = scrapy.Field()    # Renamed from 'date'
    open_date = scrapy.Field()
    closing_date = scrapy.Field()    # Renamed from 'close_date'
    link = scrapy.Field()
