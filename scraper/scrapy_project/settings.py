# filepath: /C:/Users/Zack/Desktop/School stuff/Sheet_Metal_Project/sheet_metal_scraper/scraper/scrapy_project/settings.py

BOT_NAME = 'scrapy_project'
SPIDER_MODULES = ['scrapy_project.spiders']
NEWSPIDER_MODULE = 'scrapy_project.spiders'

ITEM_PIPELINES = {
    'scrapy_project.pipelines.TenderPipeline': 300,
}

# Schedule the spider to run twice a week
# This can be done using a task scheduler or cron job outside of Scrapy