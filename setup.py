#!/usr/bin/env python

from setuptools import setup

setup(name='cloudkey',
      description='Dailymotion Cloud API client library',
      author='Dailymotion',
      url='http://github.com/dailymotion/cloudkey-py',
      version='1.0',
      install_requires=['simplejson>=2.0.9', 'pycurl>=7.19.0'],
      zip_safe=True,
      test_suite='tests')

