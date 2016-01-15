# -*- coding: utf-8 -*-
from datetime import datetime
from pyjobs_crawlers.spiders import JobSpider
from pyjobs_crawlers.items import JobItem
from scrapy import Request


class RemixJobsSpider(JobSpider):

    name = 'remixjobs'
    start_urls = ['https://remixjobs.com/Emploi-python']

    def parse_job_list_page(self, response):
        self.get_connector().log(self.name, self.ACTION_CRAWL_LIST, response.url)

        print 'crawling ...'
        # print response.body
        for job in response.css('li.job-item'):
            # first we check url. If the job exists, then skip crawling
            # (it means that the page has already been crawled
            relative_url = job.css('h3.job-title > a').xpath('@href').extract_first()
            url = self._build_url(response, relative_url)

            print 'URL IS...', url
            if self.get_connector().job_exist(url):
                self.get_connector().log(self.name, self.ACTION_MARKER_FOUND, url)
                print '-> ALREADY FOUND :-('
                return

            yield Request(url, self.parse_job_page)

        # TODO - Activate other pages
        next_page_url_xpath = '//div[@class="pagination"]/a[@class="next-link"]/@href'
        next_page_url = response.xpath(next_page_url_xpath)[0].extract()
        next_url = self._build_url(response, next_page_url)
        yield Request(url=next_url)

    def parse_job_page(self, response):
        self.get_connector().log(self.name, self.ACTION_CRAWL_JOB, response.url)

        job_node = response.css('div.job-title')

        url = response.url
        title = job_node.css('div.job-title > h1').xpath('text()').extract_first()

        job_infos = job_node.css('ul.job-infos')[0]
        company_name = job_infos.xpath('./li[1]/a/text()').extract_first().strip().rstrip(',')
        if not company_name:
            company_name = job_infos.xpath('./li[1]/text()').extract_first().strip().rstrip(',')

        company_url = job_infos.xpath('./li[1]/a/@href').extract_first().strip()

        address = job_infos.xpath('./li[4]/text()').extract_first().strip().rstrip(',')
        description = job_node.css('div.job-description').extract()

        # the_date = TODO
        # 19 mars 2015,
        #
        # thedate_xpath = './div[@id="content-core"]/div[@id="content-core"]/div[@class="discreet"]/text()'
        # # print 'DATE IS', job_node.xpath(thedate_xpath)[0].extract().strip().splitlines()
        # thedate = job_node.xpath(thedate_xpath)[0].extract().strip().splitlines()[0].strip().replace(u'Créé le ', '')
        # # Now date is formatted as "14/10/2015 13:17"
        # thedatetime = datetime.strptime(thedate, '%d/%m/%Y %H:%M')
        # publication_datetime = thedatetime


        item = JobItem()
        item['title'] = title
        item['address'] = address
        item['url'] = url  # used as uid
        item['publication_datetime'] = datetime.now()  # TODO
        item['source'] = self.name
        item['company'] = company_name
        item['company_url'] = company_url
        item['initial_crawl_datetime'] = datetime.now()
        item['description'] = description
        item['status'] = JobItem.CrawlStatus.COMPLETED

        yield item
