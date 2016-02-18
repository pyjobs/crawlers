# -*- coding: utf-8 -*-
from datetime import datetime

from pyjobs_crawlers.spiders import JobSpider, JobSource


class AlsaCreationsSpider(JobSpider):

    name = u'alsacreations'
    start_urls = ['http://emploi.alsacreations.com/index.php?action=q&q=python&table=tout&region=']
    # start_urls = [u'http://emploi.alsacreations.com/']
    label = u'Alsa Creations'
    url = u'http://emploi.alsacreations.com'
    logo_url = u'http://cdn.alsacreations.net/css/img/logo-alsacreations-com-2014.png'

    _crawl_parameters = {
        'from_page_enabled': True,
        'from_list__jobs_lists__css': 'table.offre',
        'from_list__jobs__css': 'td.mlink',
        'from_list__url__css': 'td.mlink a.intitule::attr(href)',
        'from_list__next_page__css': '',
        'from_list__title__css': 'td.mlink a.intitule::text',

        'from_page__container__css': 'div.fiche',
        'from_page__title__css': '#premier h2[itemprop=title]',
        'from_page__publication_datetime__css': 'p.navinfo time::attr(datetime)',
        'from_page__company__css': '#second h3.nom::text',
        'from_page__company_url__css': '#second a[itemprop=url]::attr(href)',
        'from_page__address__css': '#premier b[itemprop=jobLocation]::text',
        'from_page__description__css': '#premier p[itemprop=description]',
        'from_page__tags__css': '#premier p[itemprop=skills] b::text',
    }

    def _get_from_page__publication_datetime(self, job_node):
        date_text = self._extract_first(job_node, 'from_page__publication_datetime')
        if date_text:
            return date_text
        return super(AlsaCreationsSpider, self)._get_from_list__publication_datetime(job_node)

    def _get_from_page__tags(self, job_node):
        # TODO - 2016-02-18 - D.A.
        # Use the standard tags methods to extract tags (according to base list
        tags = self._extract_all(job_node, 'from_page__tags')
        if tags:
            return tags
        return super(AlsaCreationsSpider, self)._get_from_page__tags(job_node)


# N'oubliez pas cette ligne
source = JobSource.from_job_spider(AlsaCreationsSpider)
