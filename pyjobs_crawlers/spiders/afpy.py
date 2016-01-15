# -*- coding: utf-8 -*-
from datetime import datetime
from scrapy import Request
from pyjobs_crawlers.spiders import JobSpider
from pyjobs_crawlers.items import JobItem


class AfpyJobSpider(JobSpider):

    name = 'afpy'
    start_urls = ['http://www.afpy.org/jobs']

    _crawl_parameters = {
        'job_list_xpath': '//div[@class="jobitem"]',
        'job_list_element_url_xpath': './a/@href',
        'job_list_next_page_xpath': '//div[@class="listingBar"]/span[@class="next"]/a/@href',
        'job_node_xpath': '//div[@id="content"]',
        'job_title_xpath': './h1[@id="parent-fieldname-title"]/text()',
        'job_publication_date_xpath': './div[@id="content-core"]/div[@id="content-core"]/div[@class="discreet"]/text()',
        'job_company_name_xpath': ('.//h4/a/text()', './/h4/text()'),
        'job_company_url_xpath': './div[@id="content-core"]/div[@id="content-core"]/h4/a/@href',
        'job_address_xpath': './/h4[1]/following-sibling::div[@class="row"]/text()',
        'job_description_xpath': './div[@id="content-core"]/div[@id="content-core"]',
        'job_tags_xpath': './div[@id="content-core"]/div[@id="content-core"]'
    }

    # def parse_job_list_page(self, response):
    #     self.get_connector().log(self.name, self.ACTION_CRAWL_LIST, response.url)
    #
    #     for job in response.xpath('//div[@class="jobitem"]'):
    #         # first we check url. If the job exists, then skip crawling
    #         # (it means that the page has already been crawled
    #         url_xpath = './a/@href'
    #         url = job.xpath(url_xpath)[0].extract()
    #
    #         if self.get_connector().job_exist(url):
    #             self.get_connector().log(self.name, self.ACTION_MARKER_FOUND, url)
    #             return
    #
    #         yield Request(url, self.parse_job_page)
    #
    #     next_page_url_xpath = '//div[@class="listingBar"]/span[@class="next"]/a/@href'
    #     next_page_url = response.xpath(next_page_url_xpath)[0].extract()
    #     yield Request(url=next_page_url)


    def _get_job_title(self, job_container):
        job_title_xpath = self._get_parameter('job_title_xpath')
        title_lines = job_container.xpath(job_title_xpath)[0].extract().strip().splitlines()
        title = u''
        for line in title_lines:
            if line.strip() != u'':
                title += line
        return title

    def _get_job_publication_date(self, job_container):
        job_publication_date_xpath = self._get_parameter('job_publication_date_xpath')
        try:
            date_text = job_container.xpath(job_publication_date_xpath)[0].extract()\
                .strip().splitlines()[0].strip().replace(u'Créé le ', '')
            return datetime.strptime(date_text, '%d/%m/%Y %H:%M')
        except Exception:
            return super(AfpyJobSpider, self)._get_job_publication_date(job_container)

    def parse_job_page__(self, response):
        self.get_connector().log(self.name, self.ACTION_CRAWL_JOB, response.url)

        job_node = response.xpath('//div[@id="content"]')[0]

        url = response.url

        title_xpath = './h1[@id="parent-fieldname-title"]/text()'
        title_lines = job_node.xpath(title_xpath)[0].extract().strip().splitlines()
        title = u''
        for line in title_lines:
            if line.strip() != u'':
                title += line

        thedate_xpath = './div[@id="content-core"]/div[@id="content-core"]/div[@class="discreet"]/text()'
        thedate = None
        try:
            thedate = job_node.xpath(thedate_xpath)[0].extract().strip().splitlines()[0].strip().replace(u'Créé le ', '')
        except Exception:
            thedate = None

        thedatetime = datetime.strptime(thedate, '%d/%m/%Y %H:%M')
        publication_datetime = thedatetime

        company_name = job_node.xpath('.//h4/a/text()').extract_first()
        if not company_name:
            company_name = job_node.xpath('.//h4/text()').extract_first()

        company_url_xpath = './div[@id="content-core"]/div[@id="content-core"]/h4/a/@href'
        try:
            company_url = job_node.xpath(company_url_xpath)[0].extract()
        except:
            company_url = ''

        address = ' '.join(job_node.xpath('.//h4[1]/following-sibling::div[@class="row"]/text()').extract())

        description_xpath = './div[@id="content-core"]/div[@id="content-core"]'
        description = job_node.xpath(description_xpath).extract()

        item = JobItem()
        item['title'] = title
        item['address'] = address
        item['url'] = url  # used as uid
        item['publication_datetime'] = publication_datetime
        item['source'] = self.name
        item['company'] = company_name
        item['company_url'] = company_url
        item['initial_crawl_datetime'] = datetime.now()
        item['description'] = description

        html_content = ''.join(job_node.xpath('./div[@id="content-core"]/div[@id="content-core"]/node()').extract())
        item['tags'] = self.extract_tags(html_content)
        item['status'] = JobItem.CrawlStatus.COMPLETED

        yield item
