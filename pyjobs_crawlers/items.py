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

    def to_dict(self, clean=False):
        """

        :param clean: remove keys where value is None, []
        :return:
        """
        self_dict = dict(self)
        if 'publication_datetime' in self_dict:
            self_dict['publication_datetime'] = str(self_dict['publication_datetime'])

        if 'initial_crawl_datetime' in self_dict:
            self_dict['initial_crawl_datetime'] = str(self_dict['initial_crawl_datetime'])

        if 'tags' in self_dict:
            self_dict['tags'] = [tag.tag for tag in list(self_dict['tags'])]

        if clean:
            return dict((k, v) for k, v in self_dict.iteritems() if v)

        return self_dict
