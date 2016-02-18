# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):

    class CrawlStatus(object):
        PREFILLED = 'prefilled'
        COMPLETED = 'completed'
        INVALID = 'invalid'

    title = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()  # afpy-jobs, apec, etc

    address = scrapy.Field()

    description = scrapy.Field()
    company = scrapy.Field()
    company_url = scrapy.Field()

    publication_datetime = scrapy.Field()
    publication_datetime_is_fake = scrapy.Field()
    initial_crawl_datetime = scrapy.Field()

    status = scrapy.Field()
    tags = scrapy.Field()

    def to_dict(self):
        self_dict = dict(self)
        self_dict['publication_datetime'] = str(self_dict['publication_datetime'])
        self_dict['initial_crawl_datetime'] = str(self_dict['initial_crawl_datetime'])
        self_dict['tags'] = [tag for tag in list(self_dict['tags'])]
        return self_dict
