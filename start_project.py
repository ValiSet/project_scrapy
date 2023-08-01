from scrapy.crawler import CrawlerProcess
from spiders.Scrapy_spider import MySpider

if __name__ == "__main__":
    # Urls path
    file_path = 'urls.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        urls = [line.strip() for line in file]

    process = CrawlerProcess()
    process.crawl(MySpider, start_urls=urls)
    process.start()