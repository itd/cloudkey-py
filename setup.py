from setuptools import setup, find_packages
import os, sys

version = open("cloudkey/version.txt").read().strip()
setup(name='cloudkey',
      version=version,
      description='Dailymotion Cloud API client library',
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Dailymotion',
      author_email='',
      url='http://github.com/dailymotion/cloudkey-py',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['cloudkey'],
      include_package_data=True,
      zip_safe=False,
      py_modules = ['cloudkey',],
      install_requires=[
          'setuptools',
          'simplejson>=2.0.9',
          'pycurl>=7.19.0',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
