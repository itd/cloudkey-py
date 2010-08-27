import os
import urllib
import urllib2
import base64
try:
    import json
except ImportError:
    import simplejson as json
import pycurl
import StringIO
import string
import random
import hashlib
from time import time

class ApiException(Exception): pass
class AuthorizationRequired(ApiException): pass
class AuthenticationFailed(ApiException): pass
class NotFound(ApiException): pass
class MissingArgument(ApiException): pass
class InvalidArgument(ApiException): pass
class InvalidNamespace(Exception): pass
class InvalidMethod(ApiException): pass

class SecLevel:
    NONE      = 0
    DELEGATE  = 1 << 0
    ASNUM     = 1 << 1
    IP        = 1 << 2
    USERAGENT = 1 << 3
    USEONCE   = 1 << 4
    COUNTRY   = 1 << 5
    REFERER   = 1 << 6

class Api(object):
    base_url = 'http://api.dmcloud.net'
    cdn_url  = 'http://cdn.dmcloud.net'

    def __init__(self, login, password, base_url, cdn_url=None, owner_id=None, api_key=None, namespace=None, proxy=None, parent=None, force_auth=True):
        self.login = login
        self.password = password
        if (base_url):
            self.base_url = base_url
        if (cdn_url):
            self.cdn_url = cdn_url
        self.owner_id = owner_id
        self.api_key = api_key
        self.parent = parent
        self.proxy = proxy
        self.extra_params = {}
        if self.__class__.__name__ != 'Api' and not namespace:
            self.namespace = self.__class__.__name__.lower()
        else:
            self.namespace = namespace

        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.base_url, self.login, self.password)
        auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)

        if self.proxy:
            proxy_handler = urllib2.ProxyHandler({'http': self.proxy})
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
            url = '%s/json/%s?%s' % (self.base_url, path, params)

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
                    if self.login:
                        raise AuthenticationFailed()
                    else:
                        raise AuthorizationRequired()
                elif e.code in (204,):
                    return None
                raise ApiException(e)

            if response.code == 204:
                return None
            return json.loads(response.read())

        setattr(self, method, handler)

        return handler

    def _sign_url(self, url, secret, seclevel=None, asnum=None, ip=None, useragent=None, referers=[], countries=[], expires=None):
        # Normalize parameters
        seclevel = seclevel or SecLevel.NONE
        expires  = int(expires or time() + 7200)

        # Compute digest
        (url, unused, query) = url.partition('?')
        secparams = ''
        public_secparams = []
        if not seclevel & SecLevel.DELEGATE:
            if seclevel & SecLevel.ASNUM:
                if not asnum:
                    raise ValueError('ASNUM security level required and no AS number provided.')
                secparams += asnum
            if seclevel & SecLevel.IP:
                if not ip:
                    raise ValueError('IP security level required and no IP address provided.')
                secparams += ip
            if seclevel & SecLevel.USERAGENT:
                if not useragent:
                    raise ValueError('USERAGENT security level required and no user-agent provided.')
                secparams += useragent
            if seclevel & SecLevel.COUNTRY:
                if not countries or len(countries) == 0:
                    raise ValueError('COUNTRY security level required and no coutry list provided.')
                if type(countries) is not list:
                    raise ValueError('Invalid format for COUNTRY, should be a list of country codes.')
                if countries[0] == '-':
                    countries = '-' + ','.join(countries[1:])
                else:
                    countries = ','.join(countries)
                if not match(r'^-?(?:[a-zA-Z]{2})(:?,[a-zA-Z]{2})*$', countries):
                    raise ValueError('Invalid format for COUNTRY security level parameter.')
                public_secparams.append('cc=%s' % countries.lower())
            if seclevel & SecLevel.REFERER:
                if not referers or len(referers) == 0:
                    raise ValueError('REFERER security level required and no referer list provided.')
                if type(referers) is not list:
                    raise ValueError('Invalid format for REFERER, should be a list of url strings.')
                public_secparams.append('rf=%s' % quote_plus(' '.join([referer.replace(' ', '%20') for referer in referers])))

        public_secparams_encoded = ''
        if len(public_secparams) > 0:
            public_secparams_encoded = base64.b64encode(zlib.compress('&'.join(public_secparams)))
        rand   = ''.join(random.choice(string.ascii_lowercase + string.digits) for unused in range(8))
        digest = hashlib.md5('%d%s%d%s%s%s%s' % (seclevel, url, expires, rand, secret, secparams, public_secparams_encoded)).hexdigest()

        # Return signed URL
        return '%s?%sauth=%s-%s-%s-%s%s' % (url, (query + '&' if query else ''), expires, seclevel, rand, digest, ('-' + public_secparams_encoded if public_secparams_encoded else ''))

class User(Api):
    def whoami(self):
        if '_whoami' not in dir(self):
            self._whoami = self.user__whoami()
        return self._whoami

class File(Api):
    def upload_file(self, file):
        if not os.path.exists(file):
            raise IOError("[Errno 2] No such file or directory: '%s'" % file)
        result = self.upload()

        c = pycurl.Curl()
        c.setopt(pycurl.URL, str(result['url']))
        c.setopt(pycurl.FOLLOWLOCATION, True)
        c.setopt(pycurl.HTTPPOST, [('file', (pycurl.FORM_FILE, file))])

        if self.proxy:
            c.setopt(pycurl.PROXY, self.proxy)

        response = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, response.write)

        c.perform()
        c.close()

        return json.loads(response.getvalue())

class Media(Api):
    def get_embed_url(self, id=None, seclevel=None, asnum=None, ip=None, useragent=None, expires=None):
        if not self.owner_id or not self.api_key:
            raise MissingArgument('You must provide valid owner_id and api_key parameters in the constructor to use this method')
        url = '%s/embed/%s/%s' % (self.base_url, self.owner_id, id)
        return self._sign_url(url, self.api_key, seclevel=seclevel, asnum=asnum, ip=ip, useragent=useragent, expires=expires)

    def get_stream_url(self, id=None, preset='mp4_h264_aac', seclevel=None, asnum=None, ip=None, useragent=None, expires=None):
        if not self.owner_id or not self.api_key:
            raise MissingArgument('You must provide valid owner_id and api_key parameters in the constructor to use this method')
        url = '%s/route/%s/%s/%s.%s' % (self.cdn_url, self.owner_id, id, preset, preset.split('_')[0])
        return self._sign_url(url, self.api_key, seclevel=seclevel, asnum=asnum, ip=ip, useragent=useragent, expires=expires)

class Farm(Api): pass

class CloudKey(object):
    namespaces = {}
    loaded = False

    def __init__(self, login, password, base_url=None, cdn_url=None, owner_id=None, api_key=None, proxy=None):
        self.login = login;
        self.password = password
        self.base_url = base_url
        self.cdn_url = cdn_url
        self.owner_id = owner_id
        self.api_key = api_key
        self.proxy = proxy
        self._act_as_user = None

        if not CloudKey.loaded:
            for name, obj in globals().items():
                try:
                    if issubclass(obj, Api):
                        CloudKey.namespaces[name.lower()] = obj
                except TypeError:
                    pass
            CloudKey.loaded = True

    def act_as_user(self, username):
        self._act_as_user = username;
        if 'user' in dir(self): delattr(self, 'user') # reset whoami cache
        for namespace in CloudKey.namespaces:
            if namespace in dir(self):
                getattr(self, namespace).extra_params['__user__'] = self._act_as_user
        return self

    def __getattr__(self, namespace):
        try:
            ns_class =  CloudKey.namespaces[namespace]
        except KeyError:
            raise InvalidNamespace(namespace)
        namespace_obj = ns_class(self.login, self.password, self.base_url, self.cdn_url, self.owner_id, self.api_key, proxy=self.proxy, parent=self)
        if self._act_as_user:
            namespace_obj.extra_params['__user__'] = self._act_as_user
        setattr(self, namespace, namespace_obj);
        return namespace_obj
