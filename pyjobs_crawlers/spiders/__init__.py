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


class NotFound(Exception):
    pass


class ParameterNotFound(NotFound):
    pass


class NotCrawlable(Exception):
    pass


class Tag(object):
    def __init__(self, tag, iteration_nb=1):
        self.tag = tag
        self.weight = iteration_nb


class JobSpider(Spider):
    """Beginning of work"""
    ACTION_START = 'CRAWL_LIST_START'

    """End of work"""
    ACTION_FINISHED = 'CRAWL_LIST_FINISHED'

    """Spider close for other reason of finished"""
    ACTION_UNEXPECTED_END = 'ERROR_UNEXPECTED_END'

    """Crawling job list page"""
    ACTION_CRAWL_LIST = 'CRAWL_LIST'

    """Crawling job page"""
    ACTION_CRAWL_JOB = 'CRAWL_JOB_PAGE'

    """Marker (last crawled point) found: stop crawling"""
    ACTION_MARKER_FOUND = 'CRAWL_LIST_MARKER_FOUND'

    """Something went wrong when crawl"""
    ACTION_CRAWL_ERROR = 'ERROR_CRAWNLING'

    COMMON_TAGS = [
        u'cdi',
        u'cdd',
        u'télétravail',
        u'stage',
        u'freelance',
        u'mysql'
        u'postgresql',
        u'django'
    ]

    start_urls = []  # To be overwritten
    name = 'no-name'  # To be overwritten

    _crawl_parameters = {
        'jobs_xpath': '//body',
        'jobs_job_xpath': None,
        'jobs_job_element_url_xpath': None,
        'jobs_next_page_xpath': None,
        'job_node_xpath': '//body',
        'job_title_xpath': './h1/text()',
        'job_publication_date_xpath': None,
        'job_company_name_xpath': None,
        'job_company_url_xpath': None,
        'job_address_xpath': None,
        'job_description_xpath': None,
        'job_tags_xpath': None,
        # Css version of parameters
        'jobs_css': 'body',
        'jobs_job_css': None,
        'jobs_job_element_url_css': None,
        'jobs_next_page_css': None,
        'job_node_css': 'body',
        'job_title_css': 'h1',
        'job_publication_date_css': None,
        'job_company_name_css': None,
        'job_company_url_css': None,
        'job_address_css': None,
        'job_description_css': None,
        'job_tags_css': None,
    }

    _requireds = ('title', 'publication_datetime', 'description')

    def __init__(self, *args, **kwargs):
        super(JobSpider, self).__init__(*args, **kwargs)
        self._connector = None

    def _get_parameter(self, parameter_name, required=False):
        if not parameter_name in self._crawl_parameters \
                or not self._crawl_parameters[parameter_name]:
            if required:
                raise ParameterNotFound("Crawl Parameter \"%s\" is not set")
            return None

        return self._crawl_parameters[parameter_name]

    def _set_crawler(self, crawler):
        super(JobSpider, self)._set_crawler(crawler)
        self._connector = self.settings.get('connector')

    def get_connector(self):
        """

        :return:
        :rtype: pyjobs_crawlers.Connector
        """
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

        for jobs in self._get_jobs_lists(response):
            for job in self._get_jobs_nodes(jobs):
                # first we check url. If the job exists, then skip crawling
                # (it means that the page has already been crawled
                try:
                    url = self._get_jobs_node_url(job)
                except NotCrawlable:
                    break

                if self.get_connector().job_exist(url):
                    self.get_connector().log(self.name, self.ACTION_MARKER_FOUND, url)
                    break

                yield Request(url, self.parse_job_page)

        next_page_url = self._get_next_page_url(response)
        if next_page_url:
            yield Request(url=next_page_url)

    def parse_job_page(self, response):
        self.get_connector().log(self.name, self.ACTION_CRAWL_JOB, response.url)

        item = JobItem()

        try:
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

            tags_html = self._extract_first(job_container, 'job_tags', required=False)
            if tags_html:
                item['tags'] = self.extract_tags(tags_html)
        except NotFound, exc:
            # If required extraction fail, we log it
            self.get_connector().log(self.name, self.ACTION_CRAWL_ERROR, str(exc))

        # If some of required job properties are missing, job is INVALID
        if self._item_satisfying(item):
            item['status'] = JobItem.CrawlStatus.COMPLETED
        else:
            item['status'] = JobItem.CrawlStatus.INVALID

        yield item

    def _get_jobs_lists(self, response):
        return self._extract(response, 'jobs', required=True)

    def _get_jobs_nodes(self, response):
        return self._extract(response, 'jobs_job', required=True)

    def _get_jobs_node_url(self, jobs_node):
        return self._extract_first(jobs_node, 'jobs_job_element_url', required=True)

    def _get_next_page_url(self, response):
        return self._extract_first(response, 'jobs_next_page', required=False)

    def _get_job_container(self, response):
        return self._extract(response, 'job_node', required=True)

    def _get_job_title(self, job_container):
        return self._extract_first(job_container, 'job_title', required=True)

    def _get_job_publication_date(self, job_container):
        return datetime.datetime.now()

    def _get_job_company_name(self, job_container):
        return self._extract_first(job_container, 'job_company_name', required=False)

    def _get_job_company_url(self, job_container):
        return self._extract_first(job_container, 'job_company_url', required=False)

    def _get_job_address(self, job_container):
        return self._extract_first(job_container, 'job_address', required=False)

    def _get_job_description(self, job_container):
        return self._extract_first(job_container, 'job_description', required=True)

    def _item_satisfying(self, item):
        for required_field in self._requireds:
            if not item[required_field]:
                return False
        return True

    def _extract_first(self, container, selector_name, required=True):
        try:
            return ' '.join(self._extract(container, selector_name, required=True).extract_first().split())
        except NotFound:
            if not required:
                return None
            raise

    def _extract(self, container, selector_name, resolve_selector_name=True, type=None, required=True):
        """

        :param container:
        :param selector: xpath or tuple
        :return: Extracted node
        """

        if not resolve_selector_name and not type:
            raise Exception('You must set "type" parameter')

        if resolve_selector_name:
            type, selector = self._get_resolved_selector(selector_name)
        else:
            selector = selector_name

        if isinstance(selector, (list, tuple)):
            for selector_option in selector:
                try:
                    return self._extract(
                            container,
                            selector_option,
                            resolve_selector_name=False,
                            type=type,
                            required=required
                    )
                except NotFound:
                    pass  # We raise after iterate selectors options
            raise NotFound("Can't found value for %s" % selector_name)

        if type == 'css':
            extract = container.css(selector)
        elif type == 'xpath':
            extract = container.xpath(selector)

        if not extract:
            if required:
                raise NotFound("Can't found value for %s" % selector_name)
            else:
                return None

        # The join of splited text remove \n \t etc ...
        return extract

    def _get_resolved_selector(self, selector_name):
        """

        :param selector_name: The name of selector (withour suffix _xpath/_css)
        :return: a tuple containing ('type_of_selector', 'selector_value')
        """
        css_parameter_name = "%s_css" % selector_name
        try:
            return 'css', self._get_parameter(css_parameter_name, required=True)
        except ParameterNotFound:
            try:
                xpath_parameter_name = "%s_xpath" % selector_name
                return 'xpath', self._get_parameter(xpath_parameter_name, required=True)
            except ParameterNotFound:
                pass

        raise ParameterNotFound(
                "Crawl Parameter \"%s\" or (\"%s\") is not set" %
                (css_parameter_name, xpath_parameter_name)
        )

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
