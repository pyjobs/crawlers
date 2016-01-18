# -*- coding: utf-8 -*-

import re
from datetime import datetime
from scrapy import Request
from pyjobs_crawlers.spiders import JobSpider
from pyjobs_crawlers.items import JobItem
from pyjobs_crawlers.spiders import NotCrawlable
from pyjobs_crawlers import JobSource


source = JobSource(
    'linuxjobs',
    'LinuxJobs',
    'https://www.linuxjobs.fr/',
    'https://pbs.twimg.com/profile_images/649599776573403140/vaMrmib1_400x400.png'
)


class LolixJobSpider(JobSpider):
    name = 'linuxjobs'
    start_urls = ['https://www.linuxjobs.fr/search/python']

    _crawl_parameters = {
        'jobs_css': '.list-group',
        'jobs_job_css': ' .list-group-item',
        'jobs_job_element_url_xpath': './@href',
        'job_page_container_css': '.container',
        'job_page_title_css': 'div.container div.row:nth-child(2) h2::text',
        'job_page_publication_datetime_css': 'small.muted::text',
        'job_page_company_css': 'div.container div.row:nth-child(2) .col-md-9 h4:nth-child(3)::text',
        'job_page_company_url_css': ('div.container div.row:nth-child(2) .col-md-9 h4:nth-child(5) a::text',
                                'div.container div.row:nth-child(2) .col-md-9 h4:nth-child(5)::text'),
        'job_page_address_css': 'div.container div.row:nth-child(2) .col-md-9 h4:nth-child(4)::text',
        'job_page_description_css': 'div.container div.row:nth-child(4) div.col-md-9',
        'job_page_tags_css': 'div.container div.row:nth-child(4) div.col-md-9'
    }

    def _month_french_to_english(self, datetime_str):
        months = {
            u'janvier': u'january',
            u'février': u'february',
            u'mars': u'march',
            u'avril': u'april',
            u'mai': u'may',
            u'juin': u'june',
            u'juillet': u'july',
            u'août': u'august',
            u'septembre': u'september',
            u'octobre': u'october',
            u'novembre': u'november',
            u'décembre': u'december',

        }

        out = datetime_str
        for key, value in months.items():
            out = out.replace(key, value)
        return out

    def _get_jobs_node_url(self, jobs_node):
        if len(jobs_node.css('h4')) < 1: # If no h4, then, this is not a job
            raise NotCrawlable()
        return super(LolixJobSpider, self)._get_jobs_node_url(jobs_node)


    def _get_job_page_publication_datetime(self, job_container):
        publication_datetime_str = self._extract_first(job_container, 'job_publication_date')
        publication_datetime_str = publication_datetime_str.replace(u'Ajout\xe9e le', '')
        publication_datetime_str_english = self._month_french_to_english(publication_datetime_str)
        return datetime.strptime(publication_datetime_str_english, '%d %B %Y')

    def _get_job_page_address(self, job_container):
        address = super(LolixJobSpider, self)._get_job_address(job_container)
        if address:
            return re.sub(r'\([^)]*\)', '', address).strip() #  address is like Paris (programmeurs)
        return None
