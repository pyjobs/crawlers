# -*- coding: utf-8 -*-

import time

from datetime import datetime

from scrapy import Request

from pyjobs_crawlers.spiders import JobSpider
from pyjobs_crawlers.items import JobItem

import sqlalchemy as sqla
from pyjobsweb import model

engine = sqla.engine.create_engine('postgres://pyjobs:pyjobs@localhost/pyjobs')
engine.connect()
model.init_model(engine)

import os.path


class LolixJobSpider(JobSpider):

    JOB_OFFER_BASE_URL = 'http://fr.lolix.org/search/offre/'

    name = 'lolix'
    start_urls = ['http://fr.lolix.org/search/offre/search.php?page=0&mode=find&posteid=0&regionid=0&contratid=0']

    def parse_job_list_page(self, response):
        for job_row in response.xpath('//td[@class="Contenu"]/table[2]/tr[position()>1]'):
            # first we check url. If the job exists, then skip crawling
            # (it means that the page has already been crawled
            # url_xpath = './a/@href'
            # url_path = job_row.xpath('./td[3]/a/@href')[0].extract()
            url = u'{}{}'.format(LolixJobSpider.JOB_OFFER_BASE_URL,
                                 job_row.xpath('./td[3]/a/@href')[0].extract())

            existing = model.DBSession \
                .query(model.data.Job) \
                .filter(model.data.Job.url==url) \
                .count()

            if existing:
                return  # job already found; stop scrapying

            job = JobItem()
            job['url'] = url
            job['source'] = self.name
            job['address'] = ''
            job['status'] = JobItem.CrawlStatus.PREFILLED

            try:
                job['title'] = job_row.xpath('./td[3]/a/text()')[0].extract()
            except:
                job['title'] = u'No title'
            job['company'] = job_row.xpath('./td[2]/a/text()')[0].extract()
            job['company_url'] = ''

            publication_datetime_str = job_row.xpath('./td[1]/text()')[0].extract()
            publication_datetime = datetime.strptime(publication_datetime_str, '%d %B %Y')
            job['publication_datetime'] = publication_datetime

            job['initial_crawl_datetime'] = datetime.now()
            job['description'] = ''

            job_detail_request = Request(job['url'],
                                         callback=self.parse_job_page)
            job_detail_request.meta['item'] = job
            yield job_detail_request

        # TODO - Activate other pages
        # next_page_url_xpath = '//div[@class="listingBar"]/span[@class="next"]/a/@href'
        next_page_url_xpath = '//a[@class="T3" and text()="Page suivante ->"]/@href'
        next_page_url = self._build_url(
            response=response,
            path=response.xpath(next_page_url_xpath)[0].extract()
        )

        yield Request(url=next_page_url)

    def parse_job_page(self, response):
        job_node = response.css('td.Contenu')[0]

        job = response.meta['item']  # prefilled item
        job['status'] = JobItem.CrawlStatus.COMPLETED

        job['description'] = job_node.extract()

        job['address'] = u''
        address_lines = job_node.xpath('(//table)[last()]/tr[1]'
                                       '/td[1]/text()').extract()
        for line in address_lines:
            content = line.strip()
            if content \
                    and not self.match_str(content,
                                           self.address_forbidden_content()):
                job['address'] += content + ', '

        job['company_url'] = job_node.xpath('(//table)[last()]/tr[last()]'
                                            '/td[1]/a/@href')[0].extract()

        # FIXME - Make a better filtering on python jobs
        if job['title'].lower().find('python') <= 0:
            job['status'] = JobItem.CrawlStatus.INVALID
        else:
            yield job

    def address_forbidden_content(self):
        return [
            u'Tél',
            u'offre',
            u'Administration',
            u'BTP',
            u'Enseignement',
            u'Industrie',
            u'Informatique',
            u'Recherche',
            u'Editeur',
            u'Internet',
            u'SSII'
        ]

    def match_str(self, string, forbidden_string_items):
        for forbidden_item in forbidden_string_items:
            if string.find(forbidden_item) >= 0:
                return True

        return False