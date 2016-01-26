# -*- coding: utf-8 -*-
import datetime
import glob
import optparse
from importlib import import_module
from multiprocessing import Pool
from os.path import dirname, isfile, basename

import fasteners
from scrapy import signals
from scrapy.cmdline import _get_commands_dict, _run_command
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy.xlib.pydispatch import dispatcher
from slugify import slugify


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


def run_crawl(spider_module_name, connector, spider_error_callback=None):
    process = CrawlerProcess({
        'ITEM_PIPELINES': {
           'pyjobs_crawlers.pipelines.RecordJobPipeline': 1,
        },
        'connector': connector,
        'LOG_ENABLED': False
    })

    if spider_error_callback:
        dispatcher.connect(spider_error_callback, signals.spider_error)

    module_name = '.'.join(spider_module_name.split('.')[:-1])
    class_name = spider_module_name.split('.')[-1]

    spider_module = import_module(module_name)
    spider_class = getattr(spider_module, class_name)

    process.crawl(spider_class)
    spider = list(process.crawlers)[0].spider
    process.start()

    return spider


def crawl(site_file_name, connector_class):
    """

    Launch crawl job for JobSpider file
    TODO - B.S. - 20160115: Exploiter la doc (http://doc.scrapy.org/en/1.0/topics/practices.html#run-from-script)
                            pour réecrire cette fonction.

    :param connector: Connector with pyjobs_crawler caller
    :param site_file_name: python file considered as JobSpider
    :return:
    """
    connector = connector_class()
    cmdname = 'runspider'
    settings = get_project_settings()
    cmds = _get_commands_dict(settings=settings, inproject=True)

    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(),
                                   conflict_handler='resolve')
    cmd = cmds[cmdname]
    parser.usage = "scrapy %s %s" % (cmdname, cmd.syntax())
    parser.description = cmd.long_desc()
    settings.setdict(cmd.default_settings, priority='command')

    # Add our connector to config
    settings.set('connector', connector)

    cmd.settings = settings
    cmd.add_options(parser)
    opts, args = parser.parse_args(args=[site_file_name])
    cmd.process_options(args, opts)
    cmd.crawler_process = CrawlerProcess(settings)

    _run_command(cmd, args, opts)


def start_crawl_process(process_params):
    site_file_name, connector_class = process_params

    # Lock to prevent simultaneous crawnling process
    lock_name = "pyjobs_crawl_%s" % slugify(basename(site_file_name))
    lock = fasteners.InterProcessLock('/tmp/%s' % lock_name)
    lock_gotten = lock.acquire(blocking=False)

    try:
        if lock_gotten:
            crawl(site_file_name, connector_class)
        else:
            print("Crawl of \"%s\" already running" % site_file_name)
            # TODO - B.S. - 20160114: On le dit ailleurs (log) que le process est déjà en cours ?
    finally:
        if lock_gotten:
            lock.release()


def start_crawlers(connector_class, processes=1, debug=False):
    """

    Start spider processes

    :return:
    """
    # Creation of a process by site
    spiders_files = get_spiders_files()

    if debug:
        crawl(spiders_files[0], connector_class)
        print('debug finished')
        exit()

    # split list in x list of processes count elements
    spider_files_chunks = [spiders_files[x:x + processes] for x in range(0, len(spiders_files), processes)]

    # Start one cycle of processes by chunk
    for spider_files_chunk in spider_files_chunks:
        process_params_chunk = [(spider_file, connector_class) for spider_file in spider_files_chunk]
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