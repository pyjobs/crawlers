# -*- coding: utf-8 -*-

# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import urlparse
from scrapy.utils.response import get_base_url
from scrapy import Spider, Item, Field, Request
import datetime
from pyjobs_crawlers.items import JobItem


class Tag(object):
    def __init__(self, tag, iteration_nb=1):
        self.tag = tag
        self.weight = iteration_nb

class JobSpider(Spider):
    """
    TODO - B.S. - 20160115: Dans _get_jobs_container (et autres) on récupère le [0].
                            Tester si il y est et lever erreur (log + ?) si il n'y est pas.
                            De manière générale, tester et alerter partout où on va utiliser
                            les crawl parameters
    """

    """Beginning of work"""
    ACTION_START = 'START'

    """End of work"""
    ACTION_FINISHED = 'FINISHED'

    """Spider close for other reason of finished"""
    ACTION_UNEXPECTED_END = 'UNEXPECTED_END'

    """Crawling job list page"""
    ACTION_CRAWL_LIST = 'CRAWL_LIST'

    """Crawling job page"""
    ACTION_CRAWL_JOB = 'CRAWL_JOB_PAGE'

    """Marker (last crawled point) found: stop crawling"""
    ACTION_MARKER_FOUND = 'MARKER_FOUND'

    COMMON_TAGS = [
        u'cdi', u'cdd', u'télétravail', u'stage', u'freelance', u'mysql'
        u'postgresql', u'django'
    ]

    start_urls = []  # To be overwritten
    name = 'no-name'  # To be overwritten

    crawl_parameters = {
        'job_list_xpath': None,
        'job_list_element_url_xpath': None,
        'job_list_next_page_xpath': None,
        'job_node_xpath': '//body',
        'job_title_xpath': './h1/text()',
        'job_publication_date_xpath': None,
        'job_company_name_xpath': None,
        'job_company_url_xpath': None,
        'job_address_xpath': None,
        'job_description_xpath': None,
        'job_tags_xpath': None,
    }

    def __init__(self, *args, **kwargs):
        super(JobSpider, self).__init__(*args, **kwargs)
        self._connector = None

    def _get_parameter(self, parameter_name):
        if not self.crawl_parameters[parameter_name]:
            raise Exception("Crawl Parameter \"%s\" is not set")
        return self.crawl_parameters[parameter_name]

    def _set_crawler(self, crawler):
        super(JobSpider, self)._set_crawler(crawler)
        self._connector = self.settings.get('connector')

    def get_connector(self):
        if not self._connector:
            raise Exception("_connector attribute is not set")
        return self._connector

    def _build_url(self, response, path):
        base_url = get_base_url(response)
        return urlparse.urljoin(base_url, path)

    def parse(self, response):
        self.get_connector().log(self.name, self.ACTION_START)
        return self.parse_job_list_page(response)

    def parse_job_list_page(self, response):
        self.get_connector().log(self.name, self.ACTION_CRAWL_LIST, response.url)

        for job in self._get_jobs_nodes(response):
            # first we check url. If the job exists, then skip crawling
            # (it means that the page has already been crawled
            url = self._get_jobs_node_url(job)

            if self.get_connector().job_exist(url):
                self.get_connector().log(self.name, self.ACTION_MARKER_FOUND, url)
                return

            yield Request(url, self.parse_job_page)

        next_page_url = self._get_next_page_url(response)
        yield Request(url=next_page_url)

    def parse_job_page(self, response):
        self.get_connector().log(self.name, self.ACTION_CRAWL_JOB, response.url)

        item = JobItem()

        job_container = self._get_job_container(response)
        item['source'] = self.name
        item['initial_crawl_datetime'] = datetime.datetime.now()
        item['url'] = response.url
        item['title'] = self._get_job_title(job_container)
        item['publication_datetime'] = self._get_job_publication_date(job_container)
        item['company'] = self._get_job_company_name(job_container)
        item['company_url'] = self._get_job_company_url(job_container)
        item['address'] = self._get_job_address(job_container)
        item['description'] = self._get_job_description(job_container)

        job_tags_xpath = self._get_parameter('job_tags_xpath')
        item['tags'] = self.extract_tags(self._extract(job_container, job_tags_xpath))

        item['status'] = JobItem.CrawlStatus.COMPLETED

        yield item

    def _get_jobs_nodes(self, response):
        job_list_xpath = self._get_parameter('job_list_xpath')
        return response.xpath(job_list_xpath)

    def _get_jobs_node_url(self, jobs_node):
        job_list_element_url_xpath = self._get_parameter('job_list_element_url_xpath')
        return self._extract(jobs_node, job_list_element_url_xpath)

    def _get_next_page_url(self, response):
        job_list_next_page_xpath = self._get_parameter('job_list_next_page_xpath')
        return self._extract(response, job_list_next_page_xpath)

    def _get_job_container(self, response):
        job_node_xpath = self._get_parameter('job_node_xpath')
        return response.xpath('//div[@id="content"]')[0]

    def _get_job_title(self, job_container):
        job_title_xpath = self._get_parameter('job_title_xpath')
        return self._extract(job_container, job_title_xpath)

    def _get_job_publication_date(self, job_container):
        return datetime.datetime.now()

    def _get_job_company_name(self, job_container):
        job_company_name_xpath = self._get_parameter('job_company_name_xpath')
        return self._extract(job_container, job_company_name_xpath)

    def _get_job_company_url(self, job_container):
        job_company_url_xpath = self._get_parameter('job_company_url_xpath')
        return self._extract(job_container, job_company_url_xpath)

    def _get_job_address(self, job_container):
        job_address_xpath = self._get_parameter('job_address_xpath')
        return self._extract(job_container, job_address_xpath)

    def _get_job_description(self, job_container):
        job_description_xpath = self._get_parameter('job_description_xpath')
        return self._extract(job_container, job_description_xpath)

    def _extract(self, container, selector):
        """

        :param container:
        :param selector: xpath or tuple
        :return: Extracted text value OR None
        """
        if isinstance(selector, (list, tuple)):
            for selector_option in selector:
                extracted_value = self._extract(container, selector_option)
                if extracted_value:
                    return extracted_value

        extract = container.xpath(selector).extract_first()

        if not extract:
            return None

        # The join of splited text remove \n \t etc ...
        return ' '.join(extract.split())

    def _extract_common_tags(self, html_content):
        for tag in self.COMMON_TAGS:
            weight = html_content.count(tag)
            if weight:
                yield Tag(tag, weight)

    def extract_specific_tags(self, html_content):
        return []

    def extract_tags(self, html_content):
        html_content = html_content.lower()
        for tag in self._extract_common_tags(html_content):
            yield tag

        for tag in self.extract_specific_tags(html_content):
            yield tag

    @staticmethod
    def close(spider, reason):
        if reason == 'finished':
            spider.get_connector().log(spider.name, spider.ACTION_FINISHED)
        else:
            spider.get_connector().log(spider.name, spider.ACTION_UNEXPECTED_END, reason)
        return Spider.close(spider, reason)
