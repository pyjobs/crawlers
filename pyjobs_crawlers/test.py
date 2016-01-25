# -*- coding: utf-8 -*-
import datetime
import os
import unittest

from scrapy.http import Response, Request, HtmlResponse
from scrapy.item import Item

from pyjobs_crawlers import Connector
from tests import NotFound


class FunctionalTest(unittest.TestCase):
    pass


class SpiderTest(FunctionalTest):

    # These class attributes must be implemented. TODO - B.S. 20160125: Encapsutalte them ?
    _spider_class = None
    _spider = None
    _expected_jobs = None
    _test_dir = ''
    _dump_dir = ''
    _dump_format = '%s'
    _replace = ''

    def _crawl(self, start_file_path, fake_url, items=[]):
        """

        :param start_file_path: file path of start file
        :param fake_url: The fake url for Request
        :param items: List of jobs item to use as "job database". Default is empty list
        :return: list of job items
        """
        connector = SpiderTestConnector(items)

        request = Request(url=fake_url)
        start_response = fake_response_from_file(
                start_file_path,
                request=request,
                response_class=HtmlResponse
        )
        self._spider = self._get_prepared_spider()()
        self._spider.set_connector(connector)

        return list(self._parse_spider_response(self._spider.parse(start_response)))

    def _get_prepared_spider(self):
        """
        :return: Spider class override to manipulate founded urls
        """
        replace = self._replace
        dump_dir = self._dump_dir

        class OverridedSpider(self._spider_class):
            def _get_from_list__url(self, job_node):
                url = super(OverridedSpider, self)._get_from_list__url(job_node)
                if url:
                    url = url.replace(replace, 'file://' + dump_dir)
                return url

        OverridedSpider.__name__ = "Overrided%s" % self._spider_class.__name__

        return OverridedSpider

    def _parse_spider_response(self, spider_response):
        """
        :param spider_response: return of parse spider method
        :return: job item generator
        """



        for response_item in spider_response:
            if isinstance(response_item, Request):
                request = response_item
                file_path = self._dump_format % request.url.replace(self._replace, self._dump_dir)
                if file_path.find('file://') != -1:
                    file_path = file_path.replace('file://', '')
                response = fake_response_from_file(
                        file_path=file_path,
                        request=request,
                        response_class=HtmlResponse
                )
                # If a callback it's a job page request
                if request.callback:
                    for item in request.callback(response):
                        yield item
                # Else it's a next page
                else:
                    for job_item in self._parse_spider_response(self._spider.parse(response)):
                        yield job_item

            elif isinstance(response_item, Item):
                yield response_item

    def _get_result_html_file(self, html_file, items=[]):
        """
        :type items: list
        :param html_file: html file to start crawl
        :return: list of item jobs
        """
        return self._crawl(
                start_file_path=os.path.join(self._dump_dir, html_file),
                items=items,
                fake_url=self._start_url
        )

    def _get_job_from_expected(self, job_title):
        """
        Return a job from expected job, with title
        :param job_title: title of expected job
        :return: job dict
        """
        for job in self._expected_jobs:
            if job['title'] == job_title:
                return job
        raise Exception("Job \"%s\" not found" % job_title)

    @staticmethod
    def _get_job_from_result_with_title(result, job_title):
        """
        Extract job from result with title
        :param result: return of parse spider method
        :param job_title: title of wanted job
        :return: job item
        """
        for job in result:
            if job['title'] == job_title:
                return job
        raise NotFound("Job \"%s\" not found in results")

    def _result_contains_jobs(self, result, expected_jobs_titles):
        """
        Check results jobs with expected jobs
        :param result: return of parse spider method
        :param expected_jobs_titles: list of jobs title
        :return:
        """
        for expected_job_title in expected_jobs_titles:
            expected_job = self._get_job_from_expected(expected_job_title)
            try:
                result_job = self._get_job_from_result_with_title(result, expected_job_title)
            except NotFound:
                self.fail("Job \"%s\" not found in results" % expected_job_title)
            self._compare_jobs(expected_job, result_job)

    def _compare_jobs(self, expected_job, result_job):
        """
        Compare result job with expected job
        :param expected_job: job dict from extepected jobs
        :param result_job: job item from spider crawl
        :return:
        """
        result_job_as_dict = result_job.to_dict()
        for field_name in expected_job:
            if field_name not in result_job_as_dict:
                self.fail("Job \"%s\" has not \"%s\" field" % (str(result_job_as_dict), field_name))

            # Exception for url field (file path is not the same depending of executing machine
            if field_name == 'url':
                expected_job[field_name] = expected_job[field_name].replace(
                        '__tests_dir__',
                        'file://' + self._test_dir
                )

            self.assertEqual(
                    expected_job[field_name],
                    result_job_as_dict[field_name],
                    msg="Field \"%s\" of job \"%s\" field must be %s, actual is %s" % (
                        field_name,
                        result_job_as_dict['title'],
                        expected_job[field_name],
                        result_job_as_dict[field_name]
                    )
            )


class SpiderTestConnector(Connector):
    def __init__(self, saved_jobs=[]):
        self.saved_jobs = saved_jobs

    def get_most_recent_job_date(self, source):
        last_date = datetime.datetime(1970, 1, 1, 0, 0, 0)
        for job in self.saved_jobs:
            if job.publication_date > last_date:
                last_date = job.publication_date
        return last_date

    def add_job(self, job_item):
        self.saved_jobs.append(job_item)

    def job_exist(self, job_public_id):
        for job in self.saved_jobs:
            if job['url'] == job_public_id:
                return True
        return False


def fake_response_from_file(file_path, request, response_class=Response):
    """
    Create a Scrapy fake HTTP response from a HTML file
    :param request:
    :param file_path: Absolute path of source file.
    :param response_class:
    returns: A scrapy HTTP response which can be used for unittesting.
    """
    file_content = open(file_path, 'r').read()

    response = response_class(
            url=request.url,
            request=request,
            body=file_content
    )
    return response
