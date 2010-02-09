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


if __name__ == '__main__':

    import time

    c = DkAPI('sebest', 'sebest', 'dk_api.sebest.dev.dailymotion.com')

#    result = c.media_create()
#    print c.media_asset_set(id=result['id'], preset='source', url='http://isidev-01-01.dev.dailymotion.com/video/695/203/11302596:source.mov')
#    while True:
#        res = c.media_asset_process(id=result['id'], preset='flv_h263_mp3')
#        if res == 'Asset processing':
#            print 'ok'
#            break
#        else:
#            print 'sleeping'
#            time.sleep(5)


#    print result
#    print c.media_delete(id=result['id'])

#    result = c.media_create()
#    result = c.media_create()
#    result = c.media_create()

#    print c.media_meta_set(id=result['id'], key='title', value='mon super titre')

#    c.media_asset_set(id='4b6b0c1a1b5d4237bf000007', preset='source', url='http://isidev-01-01.dev.dailymotion.com/video/695/203/11302596:source.mov')
#    print c.media_asset_process(id='4b6b0c1a1b5d4237bf000007', preset='flv_h263_mp3')
#    print c.media_asset_process(id='4b6b0c1a1b5d4237bf000007', preset='flv_h263_mp3')
#    print c.media_asset_process(id='4b6b0c1a1b5d4237bf000007', preset='flv_h263_mp3')
#    fields = json.dumps(['assets.source.status', 'metas'])
#    filter = json.dumps({'assets.source.status' : 'ready'})
#    for i in c.media_list(filter=filter, fields=fields):
#    print c.media_info(id='4b6b24a31b5d421249000009')

#    for i in c.media_list():
#        print i

#    print c.media_asset_list(id='4b6b0c1a1b5d4237bf000007')
