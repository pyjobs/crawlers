# -*- coding: utf-8 -*-
from datetime import datetime

from pyjobs_crawlers.spiders import JobSpider, JobSource


class PoleEmploiSpider(JobSpider):

    name = u'pole_emploi'

    # start_urls = ['http://candidat.pole-emploi.fr/candidat/rechercheoffres/resultats/A_python_FRANCE_01___P__________INDIFFERENT_______________________']
    start_urls = ['https://candidat.pole-emploi.fr/offres/recherche?motsCles=python&offresPartenaires=true&rayon=10&tri=0']
    label = u'Pôle Emploi'
    url = u'http://candidat.pole-emploi.fr/'
    logo_url = u'http://www.pole-emploi.fr/accueil/file/sitemodel/pefr/images/accueil/header-logo-pole-emploi-mono.png'

    _crawl_parameters = {
        'from_page_enabled': True,
        'from_list__jobs_lists__css': '#zoneAfficherListeOffres',
        'from_list__jobs__css': 'li.result',
        'from_list__url__css': 'h2 > a::attr(href)',
        'from_list__title__css': 'h2 > a::text',
        'from_list__company__css': 'p.subtext::text',
        'from_list__next_page__css': None,
        'from_list__publication_datetime__css': 'td[itemprop="datePosted"]::text',
        'from_list__address__css': 'p.subtext > span::text',
        # FIXME - D.A. - 2016-02-19 - next page is protected by javascript
        # This is not a problem for us (we crawl every 15 minutes
        'from_page__container__css': 'div.container',
        'from_page__company__css': 'h4.t4.title::text',
        'from_page__company_url__css': 'dd > a::attr(href)',
        'from_page__title__css': 'h2.title::text',
        'from_page__publication_datetime__css': 'p.t5.title-complementary::text',  # something like :Publié le 31 mars 2017 - offre n° 052TWBT
        'from_page__company__css': '#second h3.nom::text',
        'from_page__address__css': 'p.t4.title-complementary::text',
        'from_page__description__css': 'div.modal-body',
        # 'from_page__tags__css': 'p[itemprop=description]::text',
    }

    def _get_from_list__publication_datetime(self, job_node):
        return ''

    def _get_from_list__url(self, job_node):
        # url is something like https://candidat.pole-emploi.fr:443/offres/recherche/detail/053BHRB%3bJSESSIONID_RECH_OFFRE=uF1AeKwGdCqOYVn1UWNfC1sjiNQx6QMzL5NWfKEc6ibo8pPodQmu!-1031959725
        # we need to remove the JSESSIONID_xxx part
        url = self._extract_first(job_node, 'from_list__url')
        url_parts = url.split('%3b')
        if len(url_parts) < 2:
            url_parts = url.split('%3B')

        return url_parts[0]

    def _get_from_page__publication_datetime(self, job_node):
        date_text = self._extract_first(job_node, 'from_page__publication_datetime')
        date_text = date_text.split(' - ')[0].replace(u'Publié le ', u'')
        day_id, month_in_french, year = date_text.split(' ')
        month_id = JobSpider._month_french_to_number(month_in_french)
        date_text = '{}/{}/{}'.format(day_id, month_id, year)
        if date_text:
            return datetime.strptime(date_text, '%d/%m/%Y')
        return super(PoleEmploiSpider, self)._get_from_page__publication_datetime(job_node)


# N'oubliez pas cette ligne
source = JobSource.from_job_spider(PoleEmploiSpider)

