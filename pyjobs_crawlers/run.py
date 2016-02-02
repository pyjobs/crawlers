# -*- coding: utf-8 -*-
import datetime
import glob
from contextlib import contextmanager
from importlib import import_module
from multiprocessing import Pool
from os.path import dirname, isfile, basename

import fasteners
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.xlib.pydispatch import dispatcher
from slugify import slugify

from pyjobs_crawlers.tools import get_spiders_classes


def stdout_error_callback(failure, response, spider):
    print("UNCATCH ERROR: (%s) %s:" % (response.url, str(failure.value)))
    print(str(failure))


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


def crawl_from_class_name(spider_class_name, connector, spider_error_callback=None):
    """
    Do the crawn job (see crawl function) from spider class name (eg. pyjobs_crawlers.spiders.myspider.MySpiderClass)
    :param spider_class_name:
    :param connector:
    :param spider_error_callback:
    :return:
    """
    module_name = '.'.join(spider_class_name.split('.')[:-1])
    class_name = spider_class_name.split('.')[-1]

    spider_module = import_module(module_name)
    spider_class = getattr(spider_module, class_name)

    return crawl([spider_class], connector, spider_error_callback)[0]


def crawl(spiders_classes, connector, debug=False, spider_error_callback=stdout_error_callback, scrapy_settings=None):
    """
    Launch crawl job for JobSpider class
    :param scrapy_settings: dict of setting merged with CrawlerProcess default settings
    :param debug: (bool) Activate or disable debug
    :param spider_error_callback: callback foir spider errors (see http://doc.scrapy.org/en/latest/topics/signals.html#spider-error)
    :param connector: Connector instance
    :param spiders_classes: JobSpider class list
    :return: spider instance
    """
    if debug:
        dispatcher.connect(spider_error_callback, signals.spider_error)

    settings = {
        'ITEM_PIPELINES': {
            'pyjobs_crawlers.pipelines.RecordJobPipeline': 1,
        },
        'connector': connector,
        'LOG_ENABLED': False,
        'DOWNLOAD_DELAY': 1 if not debug else 0,
    }
    if scrapy_settings:
        settings.update(scrapy_settings)

    process = CrawlerProcess(settings)

    for spider_class in spiders_classes:
        process.crawl(spider_class)

    spiders = []
    for crawler in list(process.crawlers):
        spiders.append(crawler.spider)
    process.start()

    return spiders


@contextmanager
def _get_lock(lock_name):
    # Lock to prevent simultaneous crawnling process
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

    lock_name = slugify(basename(spider_class))
    with _get_lock(lock_name) as acquired:
        if acquired:
            crawl([spider_class], connector_class, debug)
        else:
            print("Crawl process of \"%s\" already running" % lock_name)


def start_crawlers(connector_class, processes=1, debug=False):
    """

    Start spider processes

    :param processes:
    :param connector_class:
    :param debug:
    :return:
    """
    spiders_classes = get_spiders_classes()

    if processes == 0:
        connector = connector_class()
        with _get_lock('ALL') as acquired:
            if acquired:
                crawl(spiders_classes, connector, debug)
            else:
                print("Crawl process of 'ALL' already running")
            return

    # split list in x list of processes count elements
    spider_classes_chunks = [spiders_classes[x:x + processes] for x in range(0, len(spiders_classes), processes)]

    # Start one cycle of processes by chunk
    for spider_classes_chunk in spider_classes_chunks:
        process_params_chunk = [(spider_class, connector_class, debug) for spider_class in spider_classes_chunk]
        p = Pool(len(process_params_chunk))
        p.map(start_crawl_process, process_params_chunk)


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
