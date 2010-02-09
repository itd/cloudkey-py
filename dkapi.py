#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import simplejson as json

class DkAPIException(Exception): pass
class NotFound(DkAPIException): pass
class MissingArgument(DkAPIException): pass
class InvalidArgument(DkAPIException): pass


class DkAPI:

    def __init__(self, login, password, hostname):
        self.login = login
        self.password = password
        self.hostname = hostname

    def __getattr__(self, method):
        
        def handler(**kwargs):
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, 'http://%s/' % self.hostname, self.login, self.password)
            auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)

#            proxy_handler = urllib2.ProxyHandler({'http': 'http://127.0.0.1:8888/'})
#            opener = urllib2.build_opener(auth_handler, proxy_handler)
            opener = urllib2.build_opener(auth_handler)

            params = urllib.urlencode(kwargs)
            url = 'http://%s/%s?%s' % (self.hostname, method.replace('_', '.'), params)
            print url
            try:
                response = opener.open(url)
                result = json.loads(response.read())
                return result
            except urllib2.HTTPError, e:
                if e.code in (404, 400):
                    result = json.loads(e.read())
                    if result['error'] == 'not_found':
                        raise NotFound(result['message'])
                    elif result['error'] == 'missing_argument':
                        raise MissingArgument(result['message'])
                    elif result['error'] == 'invalid_argument':
                        raise InvalidArgument(result['message'])
                raise

        return handler
