#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import simplejson as json

from wapic import *

from cloudkey import newhttp

class Media(WApiC):

    def __init__(self, *args, **kwargs):
        super(Media, self).__init__(*args, **kwargs)
        self._whoami = None

    def whoami(self):
        if not self._whoami:
            self._whoami = self.user__whoami()
        return self._whoami

    def get_asset_url(self, id, preset):
        user_id = self.whoami()['id']

        if preset.rsplit('_', 1)[0] == 'jpeg_thumbnail':
            base_url = "http://static.dmcloud.net"
        else:
            base_url = "http://cdndirector.dmcloud.net/route"
        return "%s/%s/%s/%s.%s" % (base_url, user_id, id, preset, preset.split('_', 1)[0])

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

