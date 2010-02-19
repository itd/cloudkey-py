#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import simplejson as json

from dcapi import newhttp

class DcApiException(Exception): pass
class NotFound(DcApiException): pass
class MissingArgument(DcApiException): pass
class InvalidArgument(DcApiException): pass
class InvalidMethod(DcApiException): pass


class DcApi:

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

            url = 'http://%s/%s.json?%s' % (self.hostname, method.replace('_', '.'), params)
#            print url
            try:
                response = opener.open(url)
            except urllib2.HTTPError, e:
                if e.code in (404, 400):
                    result = json.loads(e.read())
                    if result['status_code'] == 404 and result['type'] == 'ApiNotFound':
                        raise NotFound()
                    elif result['status_code'] == 400 and result['type'] == 'ApiMissingParam':
                        raise MissingArgument(result['message'])
                    raise DcApiException(result)

            if response.code == 204:
                return None
            return json.loads(response.read())

        return handler
