#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import simplejson as json

class WApiCException(Exception): pass
class NotFound(WApiCException): pass
class MissingArgument(WApiCException): pass
class InvalidArgument(WApiCException): pass
class InvalidMethod(WApiCException): pass


class WApiC(object):

    def __init__(self, login, password, base_url, namespace=None, proxy=None):
        self.login = login
        self.password = password
        self.base_url = base_url
        self.proxy = proxy
        if self.__class__.__name__ != 'WApiC' and not namespace:
            self.namespace = self.__class__.__name__.lower()
        else:
            self.namespace = namespace

    def __getattr__(self, method):

        def handler(**kwargs):
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.base_url, self.login, self.password)
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

            if '__' in method:
                path = method.replace('__', '/')
            elif self.namespace:
                path = self.namespace + '/' + method
            else:
                path = method
            url = '%s/%s.json?%s' % (self.base_url, path, params)
#            print url
            try:
                response = opener.open(url)
            except urllib2.HTTPError, e:
                if e.code in (404, 400):
                    try:
                        result = json.loads(e.read())
                    except ValueError:
                        raise InvalidMethod(method)
                    if result['status_code'] == 404 and result['type'] == 'ApiNotFound':
                        raise NotFound()
                    elif result['status_code'] == 400 and result['type'] == 'ApiMissingParam':
                        raise MissingArgument(result['message'])
                elif e.code in (204,):
                    return None
                raise WApiCException(e)

            if response.code == 204:
                return None
            return json.loads(response.read())
        
        setattr(self, method, handler)

        return handler
