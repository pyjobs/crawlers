# -*- coding: utf-8 -*-
from datetime import datetime

from pyjobs_crawlers.spiders import JobSpider, JobSource


class LesJeudisSpider(JobSpider):

    name = 'lesjeudis'
    start_urls = ['http://www.lesjeudis.com/recherche?q=python']
    label = 'Lesjeudis.com'
    url = 'http://www.lesjeudis.com/'
    logo_url = 'http://img.icbdr.com/images/UniversalHeaderFooter/cb-logo-lj-2.png'

    _crawl_parameters = {
        'from_page_enabled': True,
        'from_list__next_page__css': 'ul.pagination li.arrow a::attr(href)',

        'from_list__jobs_lists__css': 'body',
        'from_list__jobs__css': 'div[itemtype="http://schema.org/JobPosting"]',
        'from_list__url__css': 'div#job-title h2 a::attr(href)',
        'from_list__title__css': 'div#job-title h2 a::text',
        'from_list__publication_datetime__css': 'span[itemprop="datePosted"]',
        'from_list__tags__css': 'p[itemprop="skills"] a::text',
        'from_list__address__css': 'span[itemprop="jobLocation"]::text',
        'from_list__company__css': 'div[itemprop="hiringOrganization"] a::text',
        # 'from_list__company_url__css': 'div[itemprop="hiringOrganization"] a::attr(href)',

        'from_page__description__css': 'div.job-content',
        'from_page__publication_datetime__css': 'p.info span:nth-child(2)',
    }

    def _get_from_list__publication_datetime(self, node):
        return datetime.now()

    def _get_from_page__publication_datetime(self, node):
        raw_date = self._extract_first(node, 'from_page__publication_datetime')
        if raw_date:  # La date est sous la forme "24 août 2015"
            raw_date_english = self._month_french_to_english(raw_date)  # On lma converti en Anglais
            return datetime.strptime(raw_date_english, '%d %B %Y')  # On extrait la date de ce texte
        return datetime.now()

# N'oubliez pas cette ligne
source = JobSource.from_job_spider(LesJeudisSpider)

