# -*- coding: utf-8 -*-
import unittest

test_modules = [
    'tests.functional.spiders.afpy.TestAfpySpider',
    'tests.functional.checks.TestChecks',
    ]

suite = unittest.TestSuite()

for t in test_modules:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

test_result = unittest.TextTestRunner().run(suite)

if test_result.failures or test_result.errors:
    exit(1)
