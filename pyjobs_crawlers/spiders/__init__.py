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


class StopCrawlJobList(StopIteration):
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

    """Job item fields will be filled by overrideable methods"""
    _job_item_fields = [
        'title',
        'publication_datetime',
        'company',
        'company_url',
        'address',
        'description',
        'tags'
    ]

    """Explicit list of available parameters"""
    _crawl_parameters = {
        # Xpath version of parameters
        'jobs_xpath': '//body',
        'jobs_job_xpath': None,
        'jobs_job_element_url_xpath': None,
        'jobs_next_page_xpath': None,

        'job_node_title_xpath': './h1/text()',
        'job_node_publication_datetime_xpath': None,
        'job_node_company_xpath': None,
        'job_node_company_url_xpath': None,
        'job_node_address_xpath': None,
        'job_node_description_xpath': None,
        'job_node_tags_xpath': None,

        'job_page_container_xpath': '//body',
        'job_page_title_xpath': './h1/text()',
        'job_page_publication_datetime_xpath': None,
        'job_page_company_xpath': None,
        'job_page_company_url_xpath': None,
        'job_page_address_xpath': None,
        'job_page_description_xpath': None,
        'job_page_tags_xpath': None,

        # Css version of parameters
        'jobs_css': 'body',
        'jobs_job_css': None,
        'jobs_job_element_url_css': None,
        'jobs_next_page_css': None,

        'job_node_container_css': 'body',
        'job_node_title_css': 'h1',
        'job_node_publication_datetime_css': None,
        'job_node_company_css': None,
        'job_node_company_url_css': None,
        'job_node_address_css': None,
        'job_node_description_css': None,
        'job_node_tags_css': None,

        'job_page_container_css': 'body',
        'job_page_title_css': 'h1',
        'job_page_publication_datetime_css': None,
        'job_page_company_css': None,
        'job_page_company_url_css': None,
        'job_page_address_css': None,
        'job_page_description_css': None,
        'job_page_tags_css': None,
    }

    _requireds = ('title', 'publication_datetime', 'description')

    def __init__(self, *args, **kwargs):
        super(JobSpider, self).__init__(*args, **kwargs)
        self._connector = None

    def _get_parameter(self, parameter_name, required=False):
        """

        :param parameter_name: name of parameter
        :param required: if parameter not found or null value will raise ParameterNotFound
        :return: mixed
        """
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

        :return: Connector
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
        """
        Pasring of job list
        """
        self.get_connector().log(self.name, self.ACTION_CRAWL_LIST, response.url)

        try:
            for jobs in self._get_jobs_lists(response):
                for job in self._get_jobs_nodes(jobs):
                    # first we check url. If the job exists, then skip crawling
                    # (it means that the page has already been crawled
                    try:
                        url = self._get_job_node_url(job)
                    except NotCrawlable:
                        break

                    if self.get_connector().job_exist(url):
                        self.get_connector().log(self.name, self.ACTION_MARKER_FOUND, url)
                        raise StopCrawlJobList()

                    request = Request(url, self.parse_job_page)
                    prefilled_job_item = self._get_prefilled_job_item(job)
                    request.meta['item'] = prefilled_job_item

                    yield request

            next_page_url = self._get_next_page_url(response)
            if next_page_url:
                yield Request(url=next_page_url)

        except StopCrawlJobList:
            pass

    def _get_prefilled_job_item(self, job_node):
        """

        :param job_node: html node containg the job
        :return: JobItem filled with founded data
        """
        job_item = JobItem()

        job_item['status'] = JobItem.CrawlStatus.PREFILLED
        job_item['source'] = self.name
        job_item['initial_crawl_datetime'] = datetime.datetime.now()

        for job_item_field in self._job_item_fields:
            job_item_method_name = "_get_job_node_%s" % job_item_field
            job_item[job_item_field] = getattr(self, job_item_method_name)(job_node)

        return job_item

    def parse_job_page(self, response):
        """
        Parsing of job page
        """
        self.get_connector().log(self.name, self.ACTION_CRAWL_JOB, response.url)

        job_item = response.meta['item']

        try:
            job_container = self._get_job_page_container(response)
            job_item['url'] = response.url

            for job_item_field in self._job_item_fields:
                if not job_item[job_item_field]: # Fill field only if not prefilled value
                    job_item_method_name = "_get_job_page_%s" % job_item_field
                    job_item[job_item_field] = getattr(self, job_item_method_name)(job_container)

        except NotFound, exc:
            # If required extraction fail, we log it
            self.get_connector().log(self.name, self.ACTION_CRAWL_ERROR, str(exc))

        # If some of required job properties are missing, job is INVALID
        if self._item_satisfying(job_item):
            job_item['status'] = JobItem.CrawlStatus.COMPLETED
            # TODO - B.S. - 20160118: Est-ce que l'on yield les INVALID ? Si non ils
            # disparaissent, si oui on les as en bdd mais est-ce pertinent ?
            # Ex. avec lolix ou si on les yield ils polluent la base
            yield job_item
        else:
            job_item['status'] = JobItem.CrawlStatus.INVALID


    #
    # START - Job list page methods
    #

    def _get_jobs_lists(self, response):
        return self._extract(response, 'jobs', required=True)

    def _get_jobs_nodes(self, response):
        return self._extract(response, 'jobs_job', required=True)

    def _get_job_node_url(self, job_node):
        return self._extract_first(job_node, 'jobs_job_element_url', required=True)

    def _get_next_page_url(self, response):
        return self._extract_first(response, 'jobs_next_page', required=False)

    def _get_job_node_title(self, job_node):
        return self._extract_first(job_node, 'job_node_title', required=True)

    def _get_job_node_publication_datetime(self, job_node):
        return datetime.datetime.now()

    def _get_job_node_company(self, job_node):
        return self._extract_first(job_node, 'job_node_company', required=False)

    def _get_job_node_company_url(self, job_node):
        return self._extract_first(job_node, 'job_node_company_url', required=False)

    def _get_job_node_address(self, job_node):
        return self._extract_first(job_node, 'job_node_address', required=False)

    def _get_job_node_description(self, job_node):
        return self._extract_first(job_node, 'job_node_description', required=False)

    def _get_job_node_tags(self, job_node):
        tags_html = self._extract_first(job_node, 'job_node_tags', required=False)
        if tags_html:
            return self.extract_tags(tags_html)
        return []

    #
    # END - Job list page methods
    #

    #
    # START - Job page methods
    #

    def _get_job_page_container(self, response):
        return self._extract(response, 'job_page_container', required=True)

    def _get_job_page_title(self, job_container):
        return self._extract_first(job_container, 'job_page_title', required=True)

    def _get_job_page_publication_datetime(self, job_container):
        return datetime.datetime.now()

    def _get_job_page_company(self, job_container):
        return self._extract_first(job_container, 'job_page_company', required=False)

    def _get_job_page_company_url(self, job_container):
        return self._extract_first(job_container, 'job_page_company_url', required=False)

    def _get_job_page_address(self, job_container):
        return self._extract_first(job_container, 'job_page_address', required=False)

    def _get_job_page_description(self, job_container):
        return self._extract_first(job_container, 'job_page_description', required=True)

    def _get_job_page_tags(self, job_container):
        tags_html = self._extract_first(job_container, 'job_page_tags', required=False)
        if tags_html:
            return self.extract_tags(tags_html)
        return []

    #
    # END - Job page methods
    #

    def _item_satisfying(self, item):
        """
        Return True if required fields are filled, or false if not.
        :param item: JobItem
        :return: bool
        """
        for required_field in self._requireds:
            if not item[required_field]:
                return False
        return True

    def _extract_first(self, container, selector_name, required=True):
        """

        :param container: html node
        :param selector_name: name of selector (without suffix '_xpath' or '_css')
        :param required: if True: if nothing to extracr raise NotFound. Else, return None
        :return: string
        """
        try:
            return ' '.join(self._extract(container, selector_name, required=True).extract_first().split())
        except NotFound:
            if not required:
                return None
            raise

    def _extract(self, container, selector_name, resolve_selector_name=True, selector_type=None, required=True):
        """

        :param container: html node
        :param selector: xpath or tuple
        :return: Extracted node
        :rtype: scrapy.selector.unified.SelectorList
        """

        if not resolve_selector_name and not selector_type:
            raise Exception('You must set "selector_type" parameter')

        if resolve_selector_name:
            selector_type, selector = self._get_resolved_selector(selector_name)
        else:
            selector = selector_name

        if isinstance(selector, (list, tuple)):
            for selector_option in selector:
                try:
                    return self._extract(
                            container,
                            selector_option,
                            resolve_selector_name=False,
                            selector_type=selector_type,
                            required=required
                    )
                except NotFound:
                    pass  # We raise after iterate selectors options
            raise NotFound("Can't found value for %s" % selector_name)

        if selector_type == 'css':
            extract = container.css(selector)
        elif selector_type == 'xpath':
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
