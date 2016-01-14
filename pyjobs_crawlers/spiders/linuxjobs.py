# -*- coding: utf-8 -*-

import re
from datetime import datetime
from scrapy import Request
from pyjobs_crawlers.spiders import JobSpider
from pyjobs_crawlers.items import JobItem


class LolixJobSpider(JobSpider):

    name = 'linuxjobs'
    start_urls = ['https://www.linuxjobs.fr/search/python']

    def _month_french_to_english(self, datetime_str):
        months = {
            u'janvier': u'january',
            u'février': u'february',
            u'mars': u'march',
            u'avril': u'april',
            u'mai': u'may',
            u'juin': u'june',
            u'juillet': u'july',
            u'août': u'august',
            u'septembre': u'september',
            u'octobre': u'october',
            u'novembre': u'november',
            u'décembre': u'december',

        }

        out = datetime_str
        for key, value in months.items():
            out = out.replace(key, value)
        return out

    def parse_job_list_page(self, response):
        i = 0
        for group in response.css('div.list-group'):
            goto_next_group = False

            for job_row in group.css('a.list-group-item'):
                if len(job_row.css('h4')) <= 0:  # If no H4, then, this is not a job
                    goto_next_group = True

                if not goto_next_group:
                    print 'ITERATION #{}'.format(i)
                    url = job_row.xpath('./@href')[0].extract()

                    if self.get_connector().job_exist(url):
                        return  # job already found; stop scrapying

                    job = JobItem()
                    job['status'] = JobItem.CrawlStatus.PREFILLED
                    job['url'] = url
                    job['source'] = self.name
                    job['title'] = job_row.css('h4 > span.job-title::text')[0].extract()
                    job['company'] = job_row.css('h4 > span.job-company::text')[0].extract()

                    publication_datetime_str = job_row.css('h4 > span.pull-right::text')[0].extract()
                    publication_datetime_str_english = self._month_french_to_english(publication_datetime_str)
                    print ('PUB DATE IS', publication_datetime_str_english)
                    publication_datetime = datetime.strptime(publication_datetime_str_english, '%d %B %Y')
                    job['publication_datetime'] = publication_datetime
                    job['initial_crawl_datetime'] = datetime.now()

                    job['address'] = ''
                    job['company_url'] = ''

                    print 'JOB IS', job
                    job_detail_request = Request(job['url'],
                                                 callback=self.parse_job_page)
                    job_detail_request.meta['item'] = job
                    yield job_detail_request

        # TODO - Activate other pages
        # next_page_url_xpath = '//a[@class="T3" and text()="Page suivante ->"]/@href'
        # next_page_url = self._build_url(
        #     response=response,
        #     path=response.xpath(next_page_url_xpath)[0].extract()
        # )
        #
        # yield Request(url=next_page_url)

    def parse_job_page(self, response):
        job = response.meta['item']  # prefilled item

        job_header = response.css('div.row')[0].css('div.col-md-9')
        job_address = job_header.xpath('.//h4[2]/text()')[0].extract()
        job['address'] = re.sub(r'\([^)]*\)', '', job_address).strip()  # address is like Paris (programmeurs)
        job['company_url'] = job_header.xpath('.//h4[3]/a/@href')[0].extract()

        job_description = job_header = response.css('div.row')[2].css('div.col-md-9').extract()
        job['description'] = job_description
        job['status'] = JobItem.CrawlStatus.COMPLETED

        print 'JOB IS NOW ===> ', job

        if JobItem.CrawlStatus.COMPLETED == job['status']:
            yield job

