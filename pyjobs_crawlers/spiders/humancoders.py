# -*- coding: utf-8 -*-
from datetime import datetime

from pyjobs_crawlers.spiders import JobSpider, JobSource


class HumanCodersSpider(JobSpider):

    name = 'human'
    start_urls = ['http://jobs.humancoders.com/python']
    label = 'Human coders'
    url = 'http://jobs.humancoders.com/'
    logo_url = 'http://jobs.humancoders.com/assets/logo-b2ddc104507a3e9f623788cf9278ba0e.png'

    _crawl_parameters = {
        'from_page_enabled': True,

        'from_list__jobs_lists__css': 'body',
        'from_list__jobs__css': 'li.job',
        'from_list__url__css': 'div.job_title h2 a::attr(href)',
        'from_list__title__css': 'div.job_title h2 a::text',
        'from_list__publication_datetime__css': 'div.date::text',
        'from_list__tags__xpath': '.',
        'from_list__company__css': 'div.company span.company_name::text',

        'from_page__container__css': 'body',
        'from_page__company_url__css': 'div.company_url a::attr(href)',
        'from_page__description__css': '#description'
    }

    def _get_from_list__publication_datetime(self, node):
        raw_date = self._extract_first(node, 'from_list__publication_datetime')
        if raw_date:  # La date est sous la forme "24 août 2015"
            raw_date_english = self._month_french_to_english(raw_date)  # On lma converti en Anglais
            return datetime.strptime(raw_date_english, '%d %B %Y')  # On extrait la date de ce texte

# N'oubliez pas cette ligne
source = JobSource.from_job_spider(HumanCodersSpider)
