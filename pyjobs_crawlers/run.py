# -*- coding: utf-8 -*-
from multiprocessing import Pool
import optparse
import fasteners
from scrapy.cmdline import _get_commands_dict, _run_command
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from os.path import dirname, isfile, basename
import glob
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


def crawl(site_file_name):
    """
    Launch crawl job for JobSpider file
    :param site_file_name: python file considered as JobSpider
    :return:
    """
    cmdname = 'runspider'
    settings = get_project_settings()
    cmds = _get_commands_dict(settings=settings, inproject=True)

    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(),
                                   conflict_handler='resolve')
    cmd = cmds[cmdname]
    parser.usage = "scrapy %s %s" % (cmdname, cmd.syntax())
    parser.description = cmd.long_desc()
    settings.setdict(cmd.default_settings, priority='command')
    cmd.settings = settings
    cmd.add_options(parser)
    opts, args = parser.parse_args(args=[site_file_name])

    cmd.process_options(args, opts)
    cmd.crawler_process = CrawlerProcess(settings)

    _run_command(cmd, args, opts)


def start_crawl_process(site_file_name):
    # Lock to prevent simultaneous crawnling process
    lock_name = "pyjobs_crawl_%s" % slugify(basename(site_file_name))
    lock = fasteners.InterProcessLock('/tmp/%s' % lock_name)
    lock_gotten = lock.acquire(blocking=False)

    try:
        if lock_gotten:
            crawl(site_file_name)
        else:
            print("Crawl of \"%s\" already running" % site_file_name)
            # TODO - B.S. - 20160114: On le dit ailleurs (log) que le process est déjà en cours ?
    finally:
        if lock_gotten:
            lock.release()


def start_crawlers(processes=2):
    """

    Start spider processes

    :return:
    """
    # Creation of a process by site
    spiders_files = get_spiders_files()

    # split list in x list of processes count elements
    spiders_files_chunks = [spiders_files[x:x+processes] for x in range(0, len(spiders_files), processes)]

    # Start one cycle of processes by chunk
    for spiders_files_chunk in spiders_files_chunks:
        p = Pool(len(spiders_files_chunk))
        p.map(start_crawl_process, spiders_files_chunk)


if __name__ == '__main__':
    start_crawlers()
