# -*- coding: utf-8 -*-
from datetime import datetime

from pyjobs_crawlers.spiders import JobSpider, JobSource


class LolixJobSpider(JobSpider):

    JOB_OFFER_BASE_URL = 'http://fr.lolix.org/search/offre/'

    name = 'lolix'
    start_urls = ['http://fr.lolix.org/search/offre/search.php?page=0&mode=find&posteid=0&regionid=0&contratid=0']
    label = 'Lolix'
    url = 'http://fr.lolix.org/'
    logo_url = 'http://fr.lolix.org/img/lolix/offer.png'
    reformat_url = "{domain}/search/offre/{found_url}"

    _crawl_parameters = {
        'from_list__jobs_lists__xpath': '//body',
        'from_list__jobs__xpath': '//td[@class="Contenu"]/table[2]/tr[position()>1]',
        'from_list__url__xpath': './td[3]/a/@href',
        'from_list__next_page__xpath': '//a[@class="T3" and text()="Page suivante ->"]/@href',

        'from_list__title__xpath': './td[3]/a/text()',
        'from_list__company__xpath': './td[2]/a/text()',
        'from_list__publication_datetime__xpath': './td[1]/text()',

        'from_page__container__css': 'body',
        'from_page__description__css': 'td.Contenu',
        'from_page__company_url__xpath': '(//table)[last()]/tr[last()]/td[1]/a/@href'
    }

    def _get_from_list__url(self, job_node):
        url = super(LolixJobSpider, self)._get_from_list__url(job_node)
        if url and url.find('http') is None:
            return u"%s%s" % (self.JOB_OFFER_BASE_URL, url)
        return url

    def _get_from_list__publication_datetime(self, job_node):
        date_text = self._extract_first(job_node, 'from_list__publication_datetime')
        if date_text:
            return datetime.strptime(date_text, '%d %B %Y')
        return super(LolixJobSpider, self)._get_from_list__publication_datetime(job_node)

    def _get_from_list__next_page(self, response):
        relative_url = self._extract_first(response, 'from_list__next_page', required=False)
        if relative_url:
            return self._build_url(response=response, path=relative_url)
        return None

    def _get_from_page__address(self, job_container):
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
            # fixme
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

source = JobSource.from_job_spider(LolixJobSpider)
