.. _python-sdk:

**********
Python SDK
**********

General informations
====================

The Python library exposes all API methods described in :ref:`cloud-api` section.

You can download the python library on `GitHub <http://github.com/dailymotion/cloudkey-py>`_.

A master class named ``CloudKey`` exposes all objects (eg: :ref:`media-api`) through object attributes.

The library exposes all the remote methods of :ref:`cloud-api` and also have local methods for specific purpose like uploading files or getting signed stream URLs.

Remote methods
--------------

For instance, to call the ``list`` method from the ``media`` object, the code would be as follow

.. code-block:: python

  from cloudkey import CloudKey

  USER_ID = '4c1a4d3edede832bfd000002'
  API_KEY = '52a32c7890338770e3ea1601214c02142d297298'

  cloudkey = CloudKey(USER_ID, API_KEY, BASE_URL)
  cloudkey.media.list()

For methods expecting parameters, these must be passed as named arguments:

.. code-block:: python

   clouckey.media.list(fields=['id'], per_page=20, page=2)

The returned values are a direct mapping of the JSON structure into python's native types.

Local methods
-------------

File object
^^^^^^^^^^^

.. function:: upload_file(file)

   Upload a local file to Dailymotion Cloud using its path.

  :param file: the path of the file
  :type file: str
  :returns: A dict containing the ``url`` where the uploaded file can be accessed
  :rtype: dict

Media object
^^^^^^^^^^^^

.. function:: get_embed_url(id, seclevel=None, asnum=None, ip=None, useragent=None, expires=None)

   This method returns a signed URL to a Dailymotion Cloud player embed (see the API reference for details).

   The generated URL is perishable, and access is granted based on the provided security level bitmask.

   :param id: the id of the new media object.
   :type id: media ID
   :param seclevel: the security level bitmask (default is ``SecLevel.NONE``, see below for details).
   :type seclevel: int
   :param expires: the UNIX epoch expiration time (default is ``time() + 7200`` (2 hours from now)).
   :type expires: int

   The following arguments may be required if the ``SecLevel.DELEGATE`` option is not specified in the seclevel parameter, depending on the other options. This is not recommanded as it would probably lead to spurious access denials, mainly due to GeoIP databases discrepancies.

   :param asnum: the client's autonomous system number (default is ``None``).
   :type asnum: str
   :param ip: the client's IP adress (default is ``None``).
   :type ip: str
   :param useragent: the client's HTTP User-Agent header (default is ``None``).
   :type useragent: str

   Example::

      // Create an embed URL limited only to the AS of the end-user and valid for 1 hour
      url = cloudkey.media.get_embed_url(id=media['id'], seclevel=SecLevel.DELEGATE | SecLevel.ASNUM, expires=time() + 3600)
   
.. function:: get_stream_url(id, preset='mp4_h264_aac', seclevel=None, asnum=None, ip=None, useragent=None, expires=None)

   This method returns a signed URL to a Dailymotion Cloud video stream (see the API reference for details).

   The generated URL is perishable, and access is granted based on the provided security level bitmask.

   :param id: the id of the new media object.
   :type id: media ID
   :param preset: the desired media asset preset name (default is ``mp4_h264_aac``).
   :type preset: str
   :param seclevel: the security level bitmask (default is ``SecLevel.NONE``, see below for details).
   :type seclevel: int
   :param expires: the UNIX epoch expiration time (default is ``time() + 7200`` (2 hours from now)).
   :type expires: int

   The following arguments may be required if the ``SecLevel.DELEGATE`` option is not specified in the seclevel parameter, depending on the other options. This is not recommanded as it would probably lead to spurious access denials, mainly due to GeoIP databases discrepancies.

   :param asnum: the client's autonomous system number (default is ``None``).
   :type asnum: str
   :param ip: the client's IP adress (default is ``None``).
   :type ip: str
   :param useragent: the client's HTTP User-Agent header (default is ``None``).
   :type useragent: str


Quick Tour
==========


Security level options
======================

The security level defines the mechanism used by the Dailymotion Cloud architecture to ensure a mediastream
URL access will be limited to a single user or a group of users. The different (combinable) options are:

 - ``SecLevel.NONE``: the URL access is granted to everyone.
 - ``SecLevel.ASNUM``: the URL access is granted to the specified AS number only. AS numbers stands for 'Autonomous System number' and roughly map groups of IP to telcos and large organizations on the Internet (each ISP has its own AS number for instance, Dailyotion's AS number is AS41690).
 - ``SecLevel.IP``: the URL access is granted to the specified IP address only. This option may lead to spurious access denials as some users are load-balanced behind multiple proxies when accessing the Internet (this is mostly the case with ISPs and large organizations).
 - ``SecLevel.USERAGENT``: the URL access is granted to users sending the specified User-Agent HTTP header only.
 - ``SecLevel.DELEGATE``: the ASNUM, IP and User-Agent values are to be gathered at the server side during the first URL access and don't need to be specified at the client side beforehand (this is the recommanded approach as it will ensure a 100%-accurate ASNUM recognition).
 - ``SecLevel.USEONCE``: the URL access is granted once only (using this option will probably prevent seeking from working correctly).

For more information, please refer to the Dailymotion Cloud streams security documentation.

Exceptions
==========

 * RPCException: This is the base of all exceptions

   * TransportException: When an error occured with the HTTP transport
   * SerializerError: When the Request or the Response is not valid JSON
   * InvalidRequest: When the Request is not wellformed
   * InvalidCall: When the value of the ``call`` argument is invalid
   * InvalidObject: When you access an object that doesn't exist
   * InvalidMethod: When you access a method that doesn't exist
   * InvalidParameter: When a method is called with a invalid or missing parameter
   * AuthenticationError: When authentication information is invalid

     * RateLimitExceeded: When you exceed the number of API calls on a specific timeframe

   * ApplicationException: The base class of the following exceptions

     * NotFound: When action is requested on an item that doesn't exist
     * Exists: When action is requested on an item that already exists
     * LimitExceeded: When you reach the maximum number of allowed objects.
