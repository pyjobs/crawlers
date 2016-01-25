# -*- coding: utf-8 -*-
import os
import unittest
import yaml

from pyjobs_crawlers.spiders.afpy import AfpyJobSpider
from pyjobs_crawlers.test import SpiderTest

test_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../')


class TestAfpySpider(SpiderTest):
    _spider_class = AfpyJobSpider
    _expected_jobs = yaml.load(file(test_dir + 'static/afpy/jobs.yml', 'r'))
    _test_dir = test_dir
    _dump_dir = test_dir + 'static/afpy/'
    _replace = 'http://www.afpy.org/'
    _start_url = 'http://www.afpy.org/jobs/'

    def test_initial_crawl(self):
        results = self._get_result_html_file(html_file='jobs.html')

        self.assertEqual(len(results), 7, "7 jobs must be found in jobs.html, %d found" % len(results))
        self._result_contains_jobs(results, expected_jobs_titles=[
            u"Développeur Python full stack",
            u"Développeur Python orienté FullStack",
            u"Développeur backend Python / Go H/F",
            u"Développeur web Python / Javascript",
            u"Jaccede recherche un développeur full-stack",
            u"Lead Developer Python (H/F)",
            u"DevOps Python/Go/Linux",
        ])

    def test_two_passage_with_one_more_job(self):
        items = self._get_result_html_file(html_file='jobs.html')

        self.assertEqual(len(items), 7, "7 jobs must be found in jobs.html, %d found" % len(items))
        self._result_contains_jobs(items, expected_jobs_titles=[
            u"Développeur Python full stack",
            u"Développeur Python orienté FullStack",
            u"Développeur backend Python / Go H/F",
            u"Développeur web Python / Javascript",
            u"Jaccede recherche un développeur full-stack",
            u"Lead Developer Python (H/F)",
            u"DevOps Python/Go/Linux",
        ])

        items = self._get_result_html_file(items=items, html_file='jobs_add_1.html')

        self.assertEqual(len(items), 1, "1 jobs must be found in jobs.html, %d found" % len(items))
        self._result_contains_jobs(items, expected_jobs_titles=[
            u"Développeur Python/C Confirmé (H/F)",
        ])

if __name__ == '__main__':
    unittest.main()
