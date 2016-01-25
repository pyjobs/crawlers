# -*- coding: utf-8 -*-
from pyjobs_crawlers.spiders import JobSpider
from pyjobs_crawlers import JobSource


class HumanCodersSpider(JobSpider):

    name = 'human'
    start_urls = ['http://jobs.humancoders.com/python']
    label = 'Human coders'
    url = 'http://jobs.humancoders.com/'
    logo_url = 'http://jobs.humancoders.com/assets/logo-b2ddc104507a3e9f623788cf9278ba0e.png'

    _crawl_parameters = {
        #  Paramètres à modifier après
    }

# N'oubliez pas cette ligne
source = JobSource.from_job_spider(HumanCodersSpider)
