import urllib
import urllib2
import base64
import simplejson as json
from cloudkey import newhttp

class ApiException(Exception): pass
class AuthorizationRequired(ApiException): pass
class AuthenticationFailed(ApiException): pass
class NotFound(ApiException): pass
class MissingArgument(ApiException): pass
class InvalidArgument(ApiException): pass
class InvalidNamespace(Exception): pass
class InvalidMethod(ApiException): pass

class Api(object):
    base_url = 'http://api.dmcloud.net'

    def __init__(self, login, password, base_url, namespace=None, proxy=None, force_auth=True):
        self.login = login
        self.password = password
        if (base_url):
            self.base_url = base_url
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

class User(Api):
    def whoami(self):
        if '_whoami' not in dir(self):
            self._whoami = self.user__whoami()
        return self._whoami

class File(Api):
    def upload_file(self, filename, progress_callback = None):
        result = self.upload()

        url = result['url']

        if progress_callback:
            newhttp.set_callback(progress_callback)

        if self.proxy:
            proxy_handler = urllib2.ProxyHandler({'http': self.proxy})
            opener = urllib2.build_opener(proxy_handler, newhttp.newHTTPHandler)
        else:
            opener = urllib2.build_opener(newhttp.newHTTPHandler)

        response = opener.open(url, {'file': open(filename, "rb")})
        result = json.loads(response.read())
        return result

class Media(Api): pass
class Farm(Api): pass

class CloudKey(object):
    namespaces = {'user': 'User', 'media': 'Media', 'file': 'File', 'farm': 'Farm'}

    def __init__(self, login, password, base_url=None, proxy=None):
        self.login = login;
        self.password = password
        self.base_url = base_url
        self.proxy = proxy
        self._act_as_user = None

    def act_as_user(self, username):
        self._act_as_user = username;
        if 'user' in dir(self): delattr(self, 'user') # reset whoami cache
        for namespace in CloudKey.namespaces:
            if namespace in dir(self):
                getattr(self, namespace).extra_params['__user__'] = self._act_as_user
        return self

    def __getattr__(self, namespace):
        try:
            ns_class =  globals()[CloudKey.namespaces[namespace]]
        except KeyError:
            raise InvalidNamespace(namespace)
        namespace_obj = ns_class(self.login, self.password, self.base_url, self.proxy)
        if self._act_as_user:
            namespace_obj.extra_params['__user__'] = self._act_as_user
        setattr(self, namespace, namespace_obj);
        return namespace_obj