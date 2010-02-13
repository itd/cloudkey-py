# -*- encoding: utf-8 -*-

'''HTTPHandler that supports:
 - a callback method for progress reports.
 - multipart/form-data upload without loading all the file content in memory
'''

__all__ = ('newHTTPHandler', 'newHTTSPHandler', 'set_callback')

"""
enable to upload files using multipart/form-data

import newhttp
import urllib2
urllib2.HTTPHandler = newhttp.newHTTPHandler
u = urllib2.urlopen('http://site.com/path' [, data])

data can be a mapping object or a sequence of two-elements tuples
(like in original urllib2.urlopen())
varname still need to be a string and
value can be string of a file object
eg:
  ((varname, value),
   (varname2, value),
  )
  or
  { name:  value,
    name2: value2
  }

"""

import os
import socket
import sys
import stat
import mimetypes
import mimetools
import httplib
import urllib
import urllib2
import logging

CHUNK_SIZE = 65536

logging.basicConfig()
LOG = logging.getLogger(__name__)

progress_callback = None

# mainly a copy of HTTPHandler from urllib2
class newHTTPHandler(urllib2.BaseHandler):
    
    handler_order = 200

    def http_open(self, req):
        return self.do_open(httplib.HTTP, req)

    def do_open(self, http_class, req):
        data = req.get_data()
        v_files=[]
        v_vars=[]
        # mapping object (dict)
        if req.has_data() and type(data) != str:
            if hasattr(data, 'items'):
                data = data.items()
            else:
                try:
                    if len(data) and not isinstance(data[0], tuple):
                        raise TypeError
                except TypeError:
                    ty, va, tb = sys.exc_info()
                    raise TypeError, "not a valid non-string sequence or mapping object", tb

            for (k, v) in data:
                if hasattr(v, 'read'):
                    v_files.append((k, v))
                else:
                    v_vars.append( (k, v) )
        # no file ? convert to string
        if len(v_vars) > 0 and len(v_files) == 0:
            data = urllib.urlencode(v_vars)
            v_files=[]
            v_vars=[]
        host = req.get_host()
        if not host:
            raise urllib2.URLError('no host given')

        h = http_class(host) # will parse host:port
        if req.has_data():
            h.putrequest('POST', req.get_selector())
            if not 'Content-type' in req.headers:
                if len(v_files) > 0:
                    boundary = mimetools.choose_boundary()
                    l = self._send_data(v_vars, v_files, boundary)
                    h.putheader('Content-Type',
                                'multipart/form-data; boundary=%s' % boundary)
                    h.putheader('Content-length', str(l))
                else:
                    h.putheader('Content-type',
                                'application/x-www-form-urlencoded')
                    if not 'Content-length' in req.headers:
                        h.putheader('Content-length', '%d' % len(data))
        else:
               h.putrequest('GET', req.get_selector())

        scheme, sel = urllib.splittype(req.get_selector())
        sel_host, sel_path = urllib.splithost(sel)
        h.putheader('Host', sel_host or host)
        for name, value in self.parent.addheaders:
            name = name.capitalize()
            if name not in req.headers:
                h.putheader(name, value)
        for k, v in req.headers.items():
            h.putheader(k, v)
        # httplib will attempt to connect() here.  be prepared
        # to convert a socket error to a URLError.
        try:
            h.endheaders()
        except socket.error, err:
            raise urllib2.URLError(err)

        if req.has_data():
            if len(v_files) >0:
                l = self._send_data(v_vars, v_files, boundary, h)
            elif len(v_vars) > 0:
                # if data is passed as dict ...
                data = urllib.urlencode(v_vars)
                h.send(data)
            else:
                # "normal" urllib2.urlopen()
                h.send(data)

        code, msg, hdrs = h.getreply()
        fp = h.getfile()
        if code == 200:
            resp = urllib.addinfourl(fp, hdrs, req.get_full_url())
            resp.code = code
            resp.msg = msg
            return resp
        else:
            return self.parent.error('http', req, fp, code, msg, hdrs)

    def _get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    # if sock is None, juste return the estimate size
    def _send_data(self, v_vars, v_files, boundary, sock=None):
        l = 0
        for (k, v) in v_vars:
            buffer=''
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"\r\n' % k
            buffer += '\r\n'
            buffer += v + '\r\n'
            if sock:
                sock.send(buffer)
            l += len(buffer)
        for (k, v) in v_files:
            fd = v
            file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
            name = fd.name.split('/')[-1]
            sent = 0
            if isinstance(name, unicode):
                name = name.encode('UTF-8')
            buffer=''
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (k, name)
            buffer += 'Content-Type: %s\r\n' % self._get_content_type(name)
            buffer += 'Content-Length: %s\r\n' % file_size
            buffer += '\r\n'

            l += len(buffer)
            if sock:
                sock.send(buffer)
                if hasattr(fd, 'seek'):
                    fd.seek(0)
            
                while True:
                    chunk = fd.read(CHUNK_SIZE)
                    if not chunk: break
                    sock.send(chunk)
                    if progress_callback:
                        sent += len(chunk)
                        progress = float(sent) / file_size * 100
                        progress_callback(name, progress, sent == file_size)

            l += file_size
        buffer='\r\n'
        buffer += '--%s--\r\n' % boundary
        buffer += '\r\n'
        if sock:
            sock.send(buffer)
        l += len(buffer)
        return l


class newHTTPSHandler(newHTTPHandler):
    handler_order = 200
    def https_open(self, req):
        return self.do_open(httplib.HTTPS, req)

def set_callback(method):
    global progress_callback # IGNORE:W0603

    if not callable(method):
        raise ValueError('Callback method must be callable')
    
    progress_callback = method

