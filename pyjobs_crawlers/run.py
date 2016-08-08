# -*- coding: utf-8 -*-
import datetime
import glob
from contextlib import contextmanager
from importlib import import_module
from multiprocessing import Pool
from os.path import dirname, isfile

import fasteners
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.xlib.pydispatch import dispatcher
from slugify import slugify

import pyjobs_crawlers.tools


def stdout_error_callback(failure, response, spider):
    print("UNCAUGHT ERROR: [%s] (%s) %s:"
          % (spider.name, response.url, str(failure.value)))
    print(str(failure))


def get_spiders_files(spiders_directory=None):
    """
    Returns a list of every file in spiders_directory.

    :param spiders_directory: the path where you want the search to occur. If no
    spiders_directory is specified, this function will search in this ./spiders/
    :return: returns a list of every filename in the directory spiders_directory
    """
    if spiders_directory is None:
        spiders_directory = dirname(__file__) + '/spiders/'
    return [file for file in glob.glob(spiders_directory + "/*.py")
            if isfile(file)
            and not file.endswith('__init__.py')]


def crawl_from_class_name(spider_class_path, connector,
                          spider_error_callback=None,
                          debugging_options=None, **kwargs):  # TODO: docstring
    """
    Performs a crawling operation, using the specified parameters and the
    specified spider class.

    :param spider_class_path: the classpath of the spider which will perform the
    crawling operation, eg.: pyjobs_crawlers.spiders.afpy.AfpyJobSpider
    :param connector: the connector which will be used by the spider
    :param spider_error_callback: the callback the spider will use in case an
    error that hasn't been handled occur
    :return: the spider that has been used to perform the crawling operation
    """
    module_name = '.'.join(spider_class_path.split('.')[:-1])
    class_name = spider_class_path.split('.')[-1]

    spider_module = import_module(module_name)
    spider_class = getattr(spider_module, class_name)

    return crawl([spider_class], connector,
                 spider_error_callback=spider_error_callback,
                 debugging_options=debugging_options, **kwargs)[0]


def crawl(spiders_classes, connector,
          spider_error_callback=stdout_error_callback,
          debugging_options=None, scrapy_settings=None):
    """
    Launches a crawling job for each JobSpider classes in spiders_classes.

    :param scrapy_settings: a dictionary of settings, which will be merged with
    CrawlerProcess' default settings
    settings
    :param debugging_options: enable and configure, or disable debugging. This
    parameter must be a dictionary of the following form:
    {
        'job_list_crawling': {
            'url': 'www.my_job_list_url.com',
            'recursive': (True|False),
            'single_job_offer': (True|False)
        },
        'job_offer_crawling': {
            'url': 'www.my_job_page_url.com'
        }
    }
    :param spider_error_callback: callback for unhandled spider errors, more
    details on http://doc.scrapy.org/en/latest/topics/signals.html#spider-error
    :param connector: an instance of a Connector class
    :param spiders_classes: a list of JobSpider classes
    :return: a list of the spider instances used to perform the crawling
    """
    if debugging_options:
        dispatcher.connect(spider_error_callback, signals.spider_error)

    settings = {
        'ITEM_PIPELINES': {
            'pyjobs_crawlers.pipelines.RecordJobPipeline': 1,
        },
        'connector': connector,
        'LOG_ENABLED': False,
        'DOWNLOAD_DELAY': 1 if not debugging_options else 0,
    }
    if scrapy_settings:
        settings.update(scrapy_settings)

    process = CrawlerProcess(settings)

    for spider_class in spiders_classes:
        process.crawl(spider_class, debugging_options=debugging_options)

    spiders = []
    for crawler in list(process.crawlers):
        spiders.append(crawler.spider)
    process.start()

    return spiders


@contextmanager
def _get_lock(lock_name):
    # Lock preventing simultaneous crawling processes
    lock_name = "pyjobs_crawl_%s" % lock_name
    lock = fasteners.InterProcessLock('/tmp/%s' % lock_name)
    lock_gotten = lock.acquire(blocking=False)

    try:
        yield lock_gotten
    finally:
        if lock_gotten:
            lock.release()


def start_crawl_process(process_params):
    spider_class, connector_class, debug = process_params

    lock_name = slugify(spider_class.__name__)
    with _get_lock(lock_name) as acquired:
        if acquired:
            crawl([spider_class], connector_class, debug)
        else:
            print("Crawl process of \"%s\" already running" % lock_name)


def crawl_from_spider_file_name(spider_file_name, connector,
                                spider_error_callback=None, **kwargs):
    spider_class = pyjobs_crawlers.tools.get_spider_class(spider_file_name)
    return crawl([spider_class], connector,
                 spider_error_callback=spider_error_callback, **kwargs)[0]


def start_crawlers(connector_class, num_processes=1, debug=False):
    """
    Starts a spider process for each spider class in the project

    :param num_processes: the number of simultaneous crawling processes
    :param connector_class: the connector class that should be used by the
    spiders
    :param debug: activate/deactivate debugging
    """
    spider_classes = pyjobs_crawlers.tools.get_spiders_classes()

    if num_processes == 0:
        connector = connector_class()
        with _get_lock('ALL') as acquired:
            if acquired:
                crawl(spider_classes, connector, debug)
            else:
                print("Crawl process of 'ALL' already running")
            return

    # Splits the spider_classes list in x lists of size num_processes
    spider_classes_chunks = list()
    for x in range(0, len(spider_classes), num_processes):
        spider_classes_chunks.append(spider_classes[x:x + num_processes])

    # Start num_processes number of crawling processes
    for spider_classes_chunk in spider_classes_chunks:
        process_params_chunk = [(spider_class, connector_class, debug)
                                for spider_class in spider_classes_chunk]
        p = Pool(len(process_params_chunk))
        p.map(start_crawl_process, process_params_chunk)


class Connector(object):
    """
    This class has to be used to insert caller context in pyjobs_crawler
    context.
    """

    def job_exist(self, job_public_id):
        """
        Check if the crawled job already exists in your database.

        :param job_public_id: job identifier, for instance pyjobs_crawler uses
        the job URL
        :rtype: bool
        :return: True if job exists in your database, False otherwise
        """
        raise NotImplementedError()

    def get_most_recent_job_date(self, source):
        """
        Returns the most recent publication_datetime of job for a given source.
        It will be used to stop crawling if we read an already crawled and saved
        job offer.

        :param source: source name (eg. 'afpy', 'lolix', ...)
        :type source: str
        :rtype: datetime.datetime
        :return: the most recent publication_datetime of job offers crawled from
        a given source
        """
        raise NotImplementedError()

    def add_job(self, job_item):
        """
        Saves the job offer in your database

        :param job_item: the scrapy job item
        :type job_item: pyjobs_crawlers.items.JobItem
        :return:
        """
        raise NotImplementedError()

    def log(self, source, action, more=None):
        """
        :param source: source name (eg. 'afpy', 'lolix', ...)
        :type source: str
        :param action: action identifier
        :type action: str
        :param more: more information about action
        :type more: str
        :return:
        """
        pass


class StoreConnector(Connector):
    def __init__(self):
        self._jobs = []

    def job_exist(self, job_public_id):
        return False

    def get_most_recent_job_date(self, source):
        return datetime.datetime(1970, 1, 1, 0, 0, 0)

    def add_job(self, job_item):
        self._jobs.append(job_item)

    def log(self, source, action, more=None):
        pass

    def get_jobs(self):
        return self._jobs


class StdOutputConnector(StoreConnector):
    def log(self, source, action, more=None):
        if more:
            print("LOG: (%s) %s: %s" % (source, action, more))
        else:
            print("LOG: (%s) %s" % (source, action))
