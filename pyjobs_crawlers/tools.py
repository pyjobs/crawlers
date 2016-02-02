# -*- coding: utf-8 -*-
import glob
import inspect
from genericpath import isfile
from importlib import import_module
from os.path import dirname, basename

from pyjobs_crawlers.spiders import JobSpider

common_tags = JobSpider.COMMON_TAGS
condition_tags = JobSpider.CONDITION_TAGS


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
        if not hasattr(spider_module, 'source'):
            raise Exception("Can't find \"source\" property in %s" % spider_module_name)
        spider_source = getattr(spider_module, 'source')
        sources[spider_source.id] = spider_source
    return sources


def get_spiders_classes(spiders_directory=None):
    spider_classes = []

    for spider_module_name in get_spiders_modules_names(spiders_directory):
        spider_module = import_module(spider_module_name)
        for module_attribute_name in dir(spider_module):
            module_attribute = getattr(spider_module, module_attribute_name)
            if inspect.isclass(module_attribute) \
                    and module_attribute is not JobSpider \
                    and issubclass(module_attribute, JobSpider):
                spider_classes.append(module_attribute)
                break  # We arbitrary decide it must be one spider class by file. This part is not optimally.

    return spider_classes
