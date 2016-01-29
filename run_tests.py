# -*- coding: utf-8 -*-
import unittest

from tests.functional.spiders.afpy import TestAfpySpider

suite = unittest.TestLoader().loadTestsFromTestCase(TestAfpySpider)
test_result = unittest.TextTestRunner(verbosity=2).run(suite)

if test_result.failures or test_result.errors:
    exit(1)
