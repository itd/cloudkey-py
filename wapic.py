#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import base64
import simplejson as json

class WApiCException(Exception): pass
class AuthorizationRequired(WApiCException): pass
class NotFound(WApiCException): pass
class MissingArgument(WApiCException): pass
class InvalidArgument(WApiCException): pass
class InvalidMethod(WApiCException): pass


class WApiC(object):

    def __init__(self, login, password, base_url, namespace=None, proxy=None, force_auth=True):

        self.login = login
        self.password = password
        self.base_url = base_url
        self.proxy = proxy
        self.extra_params = {}
        if self.__class__.__name__ != 'WApiC' and not namespace:
            self.namespace = self.__class__.__name__.lower()
        else:
            self.namespace = namespace

        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.base_url, self.login, self.password)
        auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)

        if self.proxy:
            proxy_handler = urllib2.ProxyHandler({'http': self.proxt})
            self.opener = urllib2.build_opener(auth_handler, proxy_handler)
        else:
            self.opener = urllib2.build_opener(auth_handler)

        self.force_auth = force_auth
        if force_auth:
            self.headers = {"Authorization": "Basic " + base64.encodestring('%s:%s' % (self.login, self.password))[:-1]}

    def __getattr__(self, method):

        def handler(**kwargs):
            for k, v in kwargs.copy().items():
                if type(v) not in (str, unicode, int, float):
                    kwargs[k] = json.dumps(v)
            kwargs.update(self.extra_params)
            params = urllib.urlencode(kwargs)

            if '__' in method:
                path = method.replace('__', '/')
            elif self.namespace:
                path = self.namespace + '/' + method
            else:
                path = method
            url = '%s/%s.json?' % (self.base_url, path)

            url = url + params
            #print url
            if self.force_auth:
                url = urllib2.Request(url, headers=self.headers)
            try:
                response = self.opener.open(url)
            except urllib2.HTTPError, e:
                if e.code in (404, 400):
                    try:
                        result = json.loads(e.read())
                    except ValueError:
                        raise InvalidMethod(method)
                    if result['status_code'] == 404 and result['type'] == 'ApiNotFound':
                        raise NotFound()
                    elif result['status_code'] == 400:
                        if result['type'] == 'ApiMissingParam':
                            raise MissingArgument(result['message'])
                        elif result['type'] == 'ApiInvalidParam':
                            raise InvalidArgument(result['message'])
                elif e.code == 401:
                    raise AuthorizationRequired()
                elif e.code in (204,):
                    return None
                raise WApiCException(e)

            if response.code == 204:
                return None
            return json.loads(response.read())
        
        setattr(self, method, handler)

        return handler
