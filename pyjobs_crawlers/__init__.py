# -*- coding: utf-8 -*-
from os.path import dirname, basename, isfile
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


class Connector(object):
    """

    """
    def job_exist(self, job_public_id):
        raise NotImplementedError()

    def add_job(self, job_item):
        raise NotImplementedError()
