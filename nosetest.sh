#!/bin/sh

nosetests --with-coverage --cover-package=cloudkey --cover-html --cover-html-dir=cover tests.py
cd cover
python -m SimpleHTTPServer 8888
