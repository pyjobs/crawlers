# -*- coding: utf-8 -*-

import re
from datetime import datetime

from pyjobs_crawlers.spiders import JobSpider, JobSource
from pyjobs_crawlers.spiders import NotCrawlable


class LinuxJobsSpider(JobSpider):

    name = 'linuxjobs'
    start_urls = ['https://www.linuxjobs.fr/search/python']
    label = 'LinuxJobs'
    url = 'https://www.linuxjobs.fr/'
    logo_url = 'https://pbs.twimg.com/profile_images/649599776573403140/vaMrmib1_400x400.png'

    _crawl_parameters = {
        'from_list__jobs_lists__css': '.container .list-group',
        'from_list__jobs__css': ' .list-group-item',
        'from_list__url__xpath': './@href',

        'from_page__container__css': '.container',
        'from_page__title__css': 'div.container div.row:nth-child(2) h2::text',
        'from_page__publication_datetime__css': 'small.muted::text',
        'from_page__company__css': 'div.container div.row:nth-child(2) .col-md-9 h4:nth-child(3)::text',
        'from_page__company_url__css': (
            'div.container div.row:nth-child(2) .col-md-9 h4:nth-child(5) a::text',
            'div.container div.row:nth-child(2) .col-md-9 h4:nth-child(5)::text'
        ),
        'from_page__address__css': 'div.container div.row:nth-child(2) .col-md-9 h4:nth-child(4)::text',
        'from_page__description__css': 'div.container div.row:nth-child(4) div.col-md-9',
        'from_page__tags__css': 'div.container div.row:nth-child(4) div.col-md-9'
    }

    def _get_from_list__jobs(self, node):
        jobs = super(LinuxJobsSpider, self)._get_from_list__jobs(node)
        if jobs:
            return jobs[::-1]  # Reverse jobs list (they are in asc order)
        return jobs

    def _get_from_list__url(self, jobs_node):
        if len(jobs_node.css('h4')) < 1: # If no h4, then, this is not a job
            raise NotCrawlable()
        return super(LinuxJobsSpider, self)._get_from_list__url(jobs_node)

    def _get_from_page__publication_datetime(self, job_container):
        publication_datetime_str = self._extract_first(job_container, 'from_page__publication_datetime')
        publication_datetime_str = publication_datetime_str.replace(u'Ajout\xe9e le', '')
        publication_datetime_str_english = self._month_french_to_english(publication_datetime_str)
        return datetime.strptime(publication_datetime_str_english, '%d %B %Y')

    def _get_from_page__address(self, job_container):
        address = super(LinuxJobsSpider, self)._get_from_page__address(job_container)
        if address:
            return re.sub(r'\([^)]*\)', '', address).strip() #  address is like Paris (programmeurs)
        return None

source = JobSource.from_job_spider(LinuxJobsSpider)
