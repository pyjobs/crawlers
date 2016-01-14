# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import pyjobs_crawlers

setup(
    name='pyjobs_crawler',
    version='0.0.1',
    packages=find_packages(),
    install_requires=['Scrapy==1.0.4',
                      'fasteners==0.14.1',
                      'python-slugify==1.1.4'],
    author='Damien Accorsi',
    author_email="contact@algoo.fr",
    description='Pyjobs crawlers',
    long_description='',
    include_package_data=True,
    url='https://github.com/pyjobs/crawlers',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7"
    ]
)
