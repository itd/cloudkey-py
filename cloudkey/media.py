#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import simplejson as json

from wapic import *

from cloudkey import newhttp

class Media(WApiC):

    def act_as_user(self, user):
        self.extra_params['__user__'] = user
        return self

    def upload(self, filename=None, progress_callback=None):
        if not filename:
            raise IllegalArgument('Arguement \'filename\' is mandatory')

        params = {'file' : open(filename, "rb")}

        if progress_callback:
            newhttp.set_callback(progress_callback)

        result = self.file__upload()
        url = result['url']

        if self.proxy:
            proxy_handler = urllib2.ProxyHandler({'http': self.proxt})
            opener = urllib2.build_opener(proxy_handler, newhttp.newHTTPHandler)
        else:
            opener = urllib2.build_opener(newhttp.newHTTPHandler)

        response = opener.open(url, params)
        result = json.loads(response.read())
        return result

