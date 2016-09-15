# -*- coding: utf-8 -*-

from pyjobs_crawlers.spiders import JobSpider, JobSource


class UrbanLinkerSpider(JobSpider):

    name = 'urbanlinker'
    start_urls = ['http://www.urbanlinker.com/offresdemploi/motcle/python/']
    label = 'Urban Linker'
    url = 'http://www.urbanlinker.com/'
    logo_url = 'http://www.urbanlinker.com/wp-content/themes/urbanlinker/images/logo-new.jpg'

    _crawl_parameters = {
        'from_page_enabled': True,
        'from_list__jobs_lists__css': '#contentoffres',
        'from_list__jobs__css': 'article.post',
        'from_list__url__css': 'h2.title-article a::attr(href)',
        'from_list__next_page__css': 'ul.bottomnav-content li.last a::attr(href)',
        'from_list__title__css': 'h2.title-article h2 a::text',
        'from_list__publication_datetime__css': '.post-info time::attr(datetime)',
        'from_page__container__css': 'article.post',
        'from_page__title__css': 'h1.title-job::text',
        'from_page__description__css': 'div.post-content',
        'from_page__address__css': 'header h1 + span::text',
    }

    def _get_from_list__publication_datetime(self, node):
        return self._extract_first(node, 'from_list__publication_datetime', required=False)

# N'oubliez pas cette ligne
source = JobSource.from_job_spider(UrbanLinkerSpider)
