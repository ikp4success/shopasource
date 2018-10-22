from shops.amazon import Amazon
from scrapy.crawler import CrawlerProcess


def get_results(search_keyword):
    amazon = Amazon()
    import pdb; pdb.set_trace()
    if __name__ == "__main__":
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        })

        process.crawl(amazon)
        process.start()
