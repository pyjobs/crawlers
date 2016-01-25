# -*- coding: utf-8 -*-
import unittest

from tests.functional.spiders.afpy import TestAfpySpider

suite = unittest.TestLoader().loadTestsFromTestCase(TestAfpySpider)
unittest.TextTestRunner(verbosity=2).run(suite)
