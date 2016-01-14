# -*- coding: utf-8 -*-
from multiprocessing import Pool
import optparse
from scrapy.cmdline import _get_commands_dict, _run_command
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from os.path import dirname, isfile
import glob


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


def start_crawlers():
    # Creation of a process by site
    # spiders_files = get_spiders_files()
    spiders_files = [get_spiders_files()[0]]
    p = Pool(len(spiders_files))
    p.map(crawl, spiders_files)


if __name__ == '__main__':
    start_crawlers()
