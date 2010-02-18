#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import simplejson as json

from dcapi import newhttp

class DcAPIException(Exception): pass
class NotFound(DcAPIException): pass
class MissingArgument(DcAPIException): pass
class InvalidArgument(DcAPIException): pass
class InvalidMethod(DcAPIException): pass


class DcAPI:

    def __init__(self, login, password, hostname, proxy=None):
        self.login = login
        self.password = password
        self.hostname = hostname
        self.proxy = proxy

    def media_upload(self, filename=None, progress_callback=None):
        if not filename:
            raise IllegalArgument('Arguement \'filename\' is mandatory')

        params = {'file' : open(filename, "rb")}

        if progress_callback:
            newhttp.set_callback(progress_callback)

        result = self.file_upload()
        url = result['url']
#        print url

        if self.proxy:
            proxy_handler = urllib2.ProxyHandler({'http': self.proxt})
            opener = urllib2.build_opener(proxy_handler, newhttp.newHTTPHandler)
        else:
            opener = urllib2.build_opener(newhttp.newHTTPHandler)

        response = opener.open(url, params)
        result = json.loads(response.read())
        return result

    def __getattr__(self, method):
        
        def handler(**kwargs):
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, 'http://%s/' % self.hostname, self.login, self.password)
            auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)

            for k, v in kwargs.copy().items():
                if type(v) not in (str, unicode, int, float):
                    kwargs[k] = json.dumps(v)
            params = urllib.urlencode(kwargs)

            if self.proxy:
                proxy_handler = urllib2.ProxyHandler({'http': self.proxt})
                opener = urllib2.build_opener(auth_handler, proxy_handler)
            else:
                opener = urllib2.build_opener(auth_handler)

            url = 'http://%s/api/1.0/rest/%s.json?%s' % (self.hostname, method.replace('_', '/'), params)
            print url
            try:
                response = opener.open(url)
            except urllib2.HTTPError, e:
                data = e.read()
                if e.code == 404:
                    if not len(data):
                        raise NotFound()
                    else:
                        raise DcAPIException(data)
                elif e.code == 400:
                    if 'Missing required parameter' in data:
                        raise MissingArgument(data)
                raise
            data = response.read()
            if data:
                return json.loads(data)
            else:
                return None

        return handler
