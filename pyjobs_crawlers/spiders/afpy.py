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
        'job_description_css': '#content-core',
        'job_tags_xpath': './div[@id="content-core"]/div[@id="content-core"]'
    }

    def _get_job_publication_date(self, job_container):
        job_publication_date_xpath = self._get_parameter('job_publication_date')
        try:
            date_text = job_container.xpath(job_publication_date_xpath)[0].extract()\
                .strip().splitlines()[0].strip().replace(u'Créé le ', '')
            return datetime.strptime(date_text, '%d/%m/%Y %H:%M')
        except Exception:
            return super(AfpyJobSpider, self)._get_job_publication_date(job_container)
