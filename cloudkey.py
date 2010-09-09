"""Dailymotion Cloud RPC loosely based on JSON-RPC"""

import os
import StringIO
import string
import random
import hashlib
from time import time
try:
    import json
except ImportError:
    import simplejson as json
import pycurl

# TODO: import the usefull methods and class in this file to make it autonomous
from cloud.rpc import HttpTransport, JSONSerializer, DefaultAuthGenerator, Client, ClientService

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

class FileService(ClientService):

    def upload_file(self, file):
        if not os.path.exists(file):
            raise IOError("[Errno 2] No such file or directory: '%s'" % file)
        result = self.upload()

        c = pycurl.Curl()
        c.setopt(pycurl.URL, str(result['url']))
        c.setopt(pycurl.FOLLOWLOCATION, True)
        c.setopt(pycurl.HTTPPOST, [('file', (pycurl.FORM_FILE, file))])

        #if self.proxy:
        #    c.setopt(pycurl.PROXY, self.proxy)

        response = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, response.write)

        c.perform()
        c.close()

        return json.loads(response.getvalue())


class MediaService(ClientService):

    def get_embed_url(self, id, seclevel=None, asnum=None, ip=None, useragent=None, expires=None):
        url = '%s/embed/%s/%s' % (self._base_url, self._user_id, id)
        return sign_url(url, self._api_key, seclevel=seclevel, asnum=asnum, ip=ip, useragent=useragent, expires=expires)

    def get_stream_url(self, id, preset='mp4_h264_aac', seclevel=None, asnum=None, ip=None, useragent=None, expires=None, cdn_url='http://cdn.dmcloud.net'):
        url = '%s/route/%s/%s/%s.%s' % (cdn_url, self._user_id, id, preset, preset.split('_')[0])
        return sign_url(url, self._api_key, seclevel=seclevel, asnum=asnum, ip=ip, useragent=useragent, expires=expires)


class CloudKey(object):

    def __init__(self, user_id, api_key, base_url='http://api.dmcloud.net'):
        self.user_id = user_id
        self.api_key = api_key
        self.base_url = base_url
        self.auth = DefaultAuthGenerator(str(user_id), str(api_key))
        t = HttpTransport(base_url + '/api')
        s = JSONSerializer()

        self.client = Client(t, s, self.auth)

    def __getattr__(self, method):
        if method == 'file':
            return FileService(self.client, method)
        if method == 'media':
            media = MediaService(self.client, method)
            media._user_id = self.user_id
            media._api_key = self.api_key
            media._base_url = self.base_url
            return media
        return ClientService(self.client, method)

    def act_as_user(self, user):
        self.auth.act_as_user(user)
