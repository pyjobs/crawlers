# -*- coding: utf-8 -*-
from datetime import datetime

from pyjobs_crawlers.spiders import JobSpider, JobSource


class PoleEmploiSpider(JobSpider):

    name = u'pole_emploi'

    start_urls = ['http://candidat.pole-emploi.fr/candidat/rechercheoffres/resultats/A_python_FRANCE_01___P__________INDIFFERENT_______________________']
    label = u'Pôle Emploi'
    url = u'http://candidat.pole-emploi.fr/'
    logo_url = u'http://www.pole-emploi.fr/accueil/file/sitemodel/pefr/images/accueil/header-logo-pole-emploi-mono.png'

    _crawl_parameters = {
        'from_page_enabled': True,
        'from_list__jobs_lists__css': 'div#offrescartezone div.result-page table.definition-table',
        'from_list__jobs__css': 'tr[itemtype="http://schema.org/JobPosting"]',
        'from_list__url__css': 'a::attr(href)',
        'from_list__title__css': 'a.title::text',
        'from_list__company__css': 'span.company span[itemprop=name]::text',
        'from_list__next_page__css': None,
        # FIXME - D.A. - 2016-02-19 - next page is protected by javascript
        # This is not a problem for us (we crawl every 15 minutes
        'from_page__container__css': '#offre-body',
        'from_page__title__css': 'h4[itemprop=title]',
        'from_page__publication_datetime__css': 'span[itemprop=datePosted]::text',
        'from_page__company__css': '#second h3.nom::text',
        'from_page__address__css': 'li[itemprop=addressRegion]::text',
        'from_page__description__css': '#offre-body p[itemprop=description]',
        'from_page__tags__css': 'p[itemprop=description]::text',
    }

    def _get_from_page__publication_datetime(self, job_node):
        date_text = self._extract_first(job_node, 'from_page__publication_datetime')
        if date_text:
            return datetime.strptime(date_text, '%d/%m/%Y')
        return super(PoleEmploiSpider, self)._get_from_page__publication_datetime(job_node)


# N'oubliez pas cette ligne
source = JobSource.from_job_spider(PoleEmploiSpider)

