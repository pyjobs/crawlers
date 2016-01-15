# -*- coding: utf-8 -*-
from os.path import dirname, isfile
import glob
from scrapy.crawler import CrawlerProcess as BaseCrawlerProcess, Crawler
from pyjobs_crawlers.spiders import JobSpider


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


class Connector(object):
    """
    Connector class have to be used to insert caller context in pyjobs_crawler context
    """
    def job_exist(self, job_public_id):
        raise NotImplementedError()

    def add_job(self, job_item):
        raise NotImplementedError()

    def log(self, source, action, more=None):
        pass


class CrawlerProcess(BaseCrawlerProcess):
    pass
