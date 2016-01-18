# -*- coding: utf-8 -*-
from datetime import datetime
from scrapy import Request
from pyjobs_crawlers.spiders import JobSpider
from pyjobs_crawlers.items import JobItem


class LolixJobSpider(JobSpider):

    JOB_OFFER_BASE_URL = 'http://fr.lolix.org/search/offre/'

    name = 'lolix'
    start_urls = ['http://fr.lolix.org/search/offre/search.php?page=0&mode=find&posteid=0&regionid=0&contratid=0']

    _crawl_parameters = {
        'jobs_xpath': '//body',
        'jobs_job_xpath': '//td[@class="Contenu"]/table[2]/tr[position()>1]',
        'jobs_job_element_url_xpath': './td[3]/a/@href',
        'jobs_next_page_xpath': '//a[@class="T3" and text()="Page suivante ->"]/@href',

        'job_node_title_xpath': './td[3]/a/text()',
        'job_node_company_xpath': './td[2]/a/text()',
        'job_node_publication_datetime_xpath': './td[1]/text()',

        'job_page_container_css': 'body',
        'job_page_description_css': 'td.Contenu',
        'job_page_company_url': '(//table)[last()]/tr[last()]/td[1]/a/@href'
    }

    def _get_job_node_url(self, job_node):
        url = super(LolixJobSpider, self)._get_job_node_url(job_node)
        return "%s%s" % (self.JOB_OFFER_BASE_URL, url)

    def _get_jobs_node_url(self, job_container):
        JOB_OFFER_BASE_URL = super(LolixJobSpider, self)._get_jobs_node_url(job_container)
        return u'{}{}'.format(self.JOB_OFFER_BASE_URL, JOB_OFFER_BASE_URL)

    def _get_job_node_publication_datetime(self, job_node):
        date_text = self._extract_first(job_node, 'job_node_publication_datetime')
        if date_text:
            return datetime.strptime(date_text, '%d %B %Y')
        return super(LolixJobSpider, self)._get_job_node_publication_datetime(job_node)

    def _get_next_page_url(self, response):
        relative_url = self._extract_first(response, 'jobs_next_page', required=False)
        if relative_url:
            return self._build_url(response=response, path=relative_url)
        return None

    def _get_job_page_address(self, job_container):
        address = u''
        address_lines = job_container.xpath('(//table)[last()]/tr[1]'
                                       '/td[1]/text()').extract()
        for line in address_lines:
            content = line.strip()
            if content \
                    and not self.match_str(content,
                                           self.address_forbidden_content()):
                address += content + ', '

        return address

    def _item_satisfying(self, item):
        satisfying = super(LolixJobSpider, self)._item_satisfying(item)
        if satisfying:
            if item['title'].lower().find('python') <= 0:
                return False
        return satisfying

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