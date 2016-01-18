# -*- coding: utf-8 -*-
from datetime import datetime
from scrapy import Request
from pyjobs_crawlers.spiders import JobSpider
from pyjobs_crawlers.items import JobItem
from pyjobs_crawlers import JobSource


source = JobSource(
    'afpy',
    'AFPY',
    'http://www.afpy.org',
    'http://www.afpy.org/logo.png'
)


class AfpyJobSpider(JobSpider):

    name = 'afpy'
    start_urls = ['http://www.afpy.org/jobs']

    _crawl_parameters = {
        'jobs_xpath': '//body',
        'jobs_job_xpath': '//div[@class="jobitem"]',
        'jobs_job_element_url_xpath': './a/@href',
        'job_list_next_page_xpath': '//div[@class="listingBar"]/span[@class="next"]/a/@href',
        'job_node_xpath': '//div[@id="content"]',
        'job_title_xpath': './h1[@id="parent-fieldname-title"]/text()',
        'job_publication_date_xpath': './div[@id="content-core"]/div[@id="content-core"]/div[@class="discreet"]/text()',
        'job_company_xpath': ('.//h4/a/text()', './/h4/text()'),
        'job_company_url_xpath': './div[@id="content-core"]/div[@id="content-core"]/h4/a/@href',
        'job_address_xpath': './/h4[1]/following-sibling::div[@class="row"]/text()',
        'job_description_css': '#content-core',
        'job_tags_xpath': './div[@id="content-core"]/div[@id="content-core"]'
    }

    def _get_job_page_publication_datetime(self, job_container):
        try:
            publication_date_text = self._extract_first(job_container, 'job_publication_date')
            if publication_date_text:
                publication_date_text_clean = publication_date_text.replace(u'Créé le ', '')
                return datetime.strptime(publication_date_text_clean, '%d/%m/%Y %H:%M')
            return super(AfpyJobSpider, self)._get_job_publication_date(job_container)
        except Exception, exc:
            self.get_connector().log(
                    self.name,
                    self.ACTION_CRAWL_ERROR,
                    "Error during publication date extraction: %s" % str(exc)
            )
            return super(AfpyJobSpider, self)._get_job_publication_date(job_container)
