"""Dailymotion Cloud RPC loosely based on JSON-RPC"""

import os
import StringIO
import string
import random
import hashlib
import datetime
import time
try:
    import json
except ImportError:
    import simplejson as json
import pycurl


#
# Common
#
class SecLevel:
    NONE      = 0
    DELEGATE  = 1 << 0
    ASNUM     = 1 << 1
    IP        = 1 << 2
    USERAGENT = 1 << 3
    USEONCE   = 1 << 4
    COUNTRY   = 1 << 5
    REFERER   = 1 << 6

def sign_url(url, secret, seclevel=None, asnum=None, ip=None, useragent=None, expires=None):
    # Normalize parameters
    seclevel = seclevel or SecLevel.NONE
    expires  = int(expires or time.time() + 7200)

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

def normalize(arg=None):
    """Normalizes an argument for signing purpose.
    
    This is used for normalizing the arguments of RPC method calls.
    
    :param arg: The argument to normalize
    
    :return: A string representating the normalized argument.
    
    .. doctest::
    
     >>> from cloud.rpc import normalize
     >>> normalize(['foo', 42, 'bar'])
     'foo42bar'
     >>> normalize({'yellow': 1, 'red': 2, 'pink' : 3})
     'pink3red2yellow1'
     >>> normalize(['foo', 42, {'yellow': 1, 'red': 2, 'pink' : 3}, 'bar'])
     'foo42pink3red2yellow1bar'    
     >>> normalize(None)
     ''
     >>> normalize([None, 1,2])
     '12'
     >>> normalize({2: [None, 1,2], 3: None, 4:5})
     '212345'
    """
    res = ''

    if type(arg) in (list, tuple):
        for i in arg:
            if type(i) in (dict, list, tuple):
                i = normalize(i)
            if i != None:
                res += str(i)
        
    elif type(arg) is dict:
        keys = arg.keys()
        keys.sort()
        for key in keys:
            i = arg[key]
            if type(i) in (dict, list, tuple):
                i = normalize(i)
            if i != None:
                res += '%s%s' % (key, i)
            else:
                res += str(key)

    elif arg != None:
        res = str(arg)

    return res

def sign(shared_secret, msg):
    """Signs a message using a shared secret.
    
    :param shared_secret: The shared secret used to sign the message
    :param msg: The message to sign
    
    :return: The signature as a string

    .. doctest::
    
     >>> from cloud.rpc import sign
     >>> sign('sEcReT_KeY', 'hello world')
     '5f048ebaf6f06576b60716dc8f815d85'
    """
    m = hashlib.md5()
    m.update(msg + shared_secret)
    return m.hexdigest()

#################################################################################
class RPCException(Exception):
    """Base class for all RPC exceptions.
    """
    code = 100

    def __init__(self, message, data=None):
        self.message = message
        self.data = data

    def __str__(self):
        msg = '%d: %s' % (self.code, self.message)
        if self.data:
            msg = '%s [%s]' % (msg, self.data)
        return msg

class ProcessorException(RPCException):
    """Base class for all Processor exceptions
    """
    code = 200

class TransportException(RPCException):
    """Exceptions in transport layer
    """
    code = 300

class AuthenticationError(RPCException):
    """Base class for all Auth exceptions.
    """
    code = 400

class RateLimitExceeded(AuthenticationError):
    code = 410

class SerializerError(RPCException):
    code = 500

class InvalidRequest(RPCException):
    code = 600

class InvalidService(InvalidRequest):
    code = 610

class InvalidMethod(InvalidRequest):
    code = 620

class InvalidParameter(InvalidRequest):
    code = 630

class ApplicationException(RPCException):
    code = 1000

class NotFound(ApplicationException):
    code = 1010

class Exists(ApplicationException):
    code = 1020

class LimitExceeded(ApplicationException):
    code = 1030

def RPCException_handler(error):
    # TODO Autogenerate this dict by introspection
    exceptions = {
        200: ProcessorException,
        300: TransportException,
        400: AuthenticationError,
        410: RateLimitExceeded,
        500: SerializerError,
        600: InvalidRequest,
        610: InvalidService,
        620: InvalidMethod,
        630: InvalidParameter,
        1000: ApplicationException,
        1010: NotFound,
        1020: Exists,
        1030: LimitExceeded,
        }

    e = exceptions.get(error['code'], RPCException)
    return e(error['message'], error.get('data', None))


class JSONEncoder(json.JSONEncoder):
    """Extends JSON encoder to handle types like datetime
    
    .. doctest::
    
     >>> import json
     >>> from datetime import datetime
     >>> from cloud.rpc import JSONEncoder
     >>> my_date = datetime(year=2010, month=04, day=11)
     >>> json.dumps(my_date, cls=JSONEncoder)
     '1270936800'
    """
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return int(time.mktime(obj.timetuple()))
        return json.JSONEncoder.default(self, obj)


class ClientService(object):

    def __init__(self, client, name):
        self._client = client
        self._name = name
        
    def __getattr__(self, method):

        def func(**kwargs):
            request = {
                'service': self._name,
                'method': method,
                'args': kwargs,
                }

            if not self._client._act_as_user:
                user_infos = self._client._user_id
            else:
                user_infos = "%s/%s" % (self._client._user_id, self._client._act_as_user)
            request['auth'] = user_infos + ':' + sign(self._client._api_key, user_infos + normalize(request))


            c = pycurl.Curl()
            c.setopt(pycurl.URL, self._client._api_endpoint)
            c.setopt(pycurl.HTTPHEADER, ["Content-Type: application/json"])

            c.setopt(pycurl.POSTFIELDS, json.dumps(request, cls=JSONEncoder))

            if self._client._proxy:
                c.setopt(pycurl.PROXY, self._client._proxy)

            response = StringIO.StringIO()
            c.setopt(pycurl.WRITEFUNCTION, response.write)
            
            try:
                c.perform()
            except pycurl.error, e:
                raise TransportException(str(e))
            c.close()

            try:
                msg = json.loads(response.getvalue())
            except (TypeError, ValueError), e:
                raise SerializerError(str(e))
            error = msg.get('error', None)
            if error:
                raise RPCException_handler(error)
            return msg.get('result')

        return func


class FileService(ClientService):

    def upload_file(self, file):
        if not os.path.exists(file):
            raise IOError("[Errno 2] No such file or directory: '%s'" % file)
        result = self.upload()

        c = pycurl.Curl()
        c.setopt(pycurl.URL, str(result['url']))
        c.setopt(pycurl.FOLLOWLOCATION, True)
        c.setopt(pycurl.HTTPPOST, [('file', (pycurl.FORM_FILE, file))])

        if self._client._proxy:
            c.setopt(pycurl.PROXY, self._client._proxy)

        response = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, response.write)

        try:
            c.perform()
        except pycurl.error, e:
            raise TransportException(str(e))
        c.close()

        return json.loads(response.getvalue())


class MediaService(ClientService):

    def get_embed_url(self, id, seclevel=None, asnum=None, ip=None, useragent=None, expires=None):
        url = '%s/embed/%s/%s' % (self._client._base_url, self._client._user_id, id)
        return sign_url(url, self._client._api_key, seclevel=seclevel, asnum=asnum, ip=ip, useragent=useragent, expires=expires)

    def get_stream_url(self, id, preset='mp4_h264_aac', seclevel=None, asnum=None, ip=None, useragent=None, expires=None, cdn_url='http://cdn.dmcloud.net'):
        url = '%s/route/%s/%s/%s.%s' % (cdn_url, self._client._user_id, id, preset, preset.split('_')[0])
        return sign_url(url, self._client._api_key, seclevel=seclevel, asnum=asnum, ip=ip, useragent=useragent, expires=expires)


class CloudKey(object):

    def __init__(self, user_id, api_key, base_url='http://api.dmcloud.net', proxy=None):
        self._user_id = user_id if user_id else ''
        self._api_key = api_key if api_key else ''
        self._base_url = base_url
        self._act_as_user = None
        self._api_endpoint =  base_url + '/api'
        self._proxy = proxy

    def __getattr__(self, method):
        if method == 'file':
            return FileService(self, method)
        if method == 'media':
            media = MediaService(self, method)
            return media
        return ClientService(self, method)

    def act_as_user(self, user):
        self._act_as_user = user
