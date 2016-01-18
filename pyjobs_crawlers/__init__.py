# -*- coding: utf-8 -*-
from os.path import dirname, isfile, basename
import glob
from scrapy.crawler import CrawlerProcess as BaseCrawlerProcess, Crawler
from pyjobs_crawlers.spiders import JobSpider
from importlib import import_module


def get_spiders_files(spiders_directory=None):
    """

    Return list of filename corresponding to JobSpider

    :param spiders_directory: Path where search JobSpiders
    :return: list of filename
    """
    if spiders_directory is None:
        spiders_directory = dirname(__file__) + '/spiders/'
    return [file for file in glob.glob(spiders_directory + "/*.py")
            if isfile(file)
            and not file.endswith('__init__.py')]


def get_spiders_modules_names(spiders_directory=None):
    modules = []
    for spider_file in get_spiders_files(spiders_directory):
        module_name = "pyjobs_crawlers.spiders.%s" % basename(spider_file.replace('.py', ''))
        modules.append(module_name)
    return modules


def get_sources(spiders_directory=None):
    sources = {}
    for spider_module_name in get_spiders_modules_names(spiders_directory):
        spider_module = import_module(spider_module_name)
        spider_source = getattr(spider_module, 'source')
        sources[spider_source.id] = spider_source
    return sources


class JobSource(object):
    def __init__(self, id, label, url, logo_url):
        self.logo_url = logo_url
        self.label = label
        self.id = id
        self.url = url


class Connector(object):
    """
    Connector class have to be used to insert caller context in pyjobs_crawler context
    """
    def job_exist(self, job_public_id):
        raise NotImplementedError()

    def get_most_recent_job_date(self, source):
        raise NotImplementedError()

    def add_job(self, job_item):
        raise NotImplementedError()

    def log(self, source, action, more=None):
        pass


class CrawlerProcess(BaseCrawlerProcess):
    pass
