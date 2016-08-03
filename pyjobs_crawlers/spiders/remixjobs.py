# -*- coding: utf-8 -*-
from datetime import datetime
from time import mktime

import feedparser
from scrapy import Request

from pyjobs_crawlers.items import JobItem
from pyjobs_crawlers.spiders import JobSpider, JobSource


class RemixJobsSpider(JobSpider):

    name = 'remixjobs'
    start_urls = ['https://remixjobs.com/rss/python']
    label = 'RemixJobs'
    url = 'https://remixjobs.com/'
    logo_url = 'https://remixjobs.com/images/press/logos/logo2-450-140.png'

    _forced_collected_field = (
        'tags', 'title', 'description', 'publication_datetime', 'company', 'address'
    )

    _crawl_parameters = {
        'from_page__tags__xpath': '.'
    }

    def __init__(self, *args, **kwargs):
        super(RemixJobsSpider, self).__init__(*args, **kwargs)
        self._last_job_date = datetime(1970, 1, 1, 0, 0, 0)

    def _set_crawler(self, crawler):
        super(RemixJobsSpider, self)._set_crawler(crawler)
        self._last_job_date = self.get_connector().get_most_recent_job_date(self.name)

    def parse_job_list_page(self, response):
        self.get_connector().log(self.name, self.ACTION_CRAWL_LIST, response.url)

        feed_parser = feedparser.parse(response.body)
        for job_entry in feed_parser.entries:
            job_url = job_entry.link
            job_publication_date = datetime.fromtimestamp(mktime(job_entry.published_parsed))

            job_publication_time = mktime(job_publication_date.timetuple())
            last_job_publication_time = mktime(self._last_job_date.timetuple())
            if job_publication_time <= last_job_publication_time:
                self.get_connector().log(self.name,
                                         self.ACTION_MARKER_FOUND,
                                         "%s <= %s" % (job_publication_time, last_job_publication_time))
                return

            prepared_job = JobItem()
            request = Request(job_url, self.parse_job_page)
            request.meta['item'] = prepared_job

            prepared_job['title'] = job_entry.title
            prepared_job['description'] = job_entry.description
            prepared_job['publication_datetime'] = job_publication_date

            yield request

    def parse_job_page(self, response):
        self.get_connector().log(self.name, self.ACTION_CRAWL_JOB, response.url)

        item = response.meta['item']  # prefilled item
        job_node = response.css('#content .layer')

        url = response.url
        # title = job_node.css('div.job-title > h1').xpath('text()').extract_first()

        job_infos = job_node.css('ul.job-infos')[0]
        company = job_infos.xpath('./li[1]/a/text()').extract_first().strip().rstrip(',')
        if not company:
            company = job_infos.xpath('./li[1]/text()').extract_first().strip().rstrip(',')

        # company_url = job_infos.xpath('./li[1]/a/@href').extract_first().strip()

        address = job_infos.xpath('./li[4]/text()').extract_first().strip().rstrip(',')
        # description = job_node.css('div.job-description').extract()

        tags_html = self._extract_first(job_node, 'from_page__tags', required=False)
        if tags_html:
            item['tags'] = self.extract_tags(tags_html)

        # 19 mars 2015,
        #
        # thedate_xpath = './div[@id="content-core"]/div[@id="content-core"]/div[@class="discreet"]/text()'
        # # print 'DATE IS', job_node.xpath(thedate_xpath)[0].extract().strip().splitlines()
        # thedate = job_node.xpath(thedate_xpath)[0].extract().strip().splitlines()[0].strip().replace(u'Créé le ', '')
        # # Now date is formatted as "14/10/2015 13:17"
        # thedatetime = datetime.strptime(thedate, '%d/%m/%Y %H:%M')
        # publication_datetime = thedatetime


        item['address'] = address
        item['url'] = url  # used as uid
        item['source'] = self.name
        item['company'] = company
        # item['company_url'] = company_url
        item['initial_crawl_datetime'] = datetime.now()
        item['status'] = JobItem.CrawlStatus.COMPLETED

        yield item

source = JobSource.from_job_spider(RemixJobsSpider)
