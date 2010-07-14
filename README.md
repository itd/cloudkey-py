Remote methods
==============

The Dailymotion Cloud API Python binding exposes all API methods described in the API reference.
A master class named `CloudKey` exposes all namespaces through object attributes. For instance,
a call to the `count` method in the `media` namespace would be as follow:

    cloudkey = CloudKey(username, password)
    result = cloudkey.media.count()

For methods expecting parameters, these must be passed as named arguments:

    media = cloudkey.media.info(id: a_media_id)

The returned values (when available) are either `dict`s (when result is a structure) or `list`s
of `dict`s (when result is a list of structures):

    # Simple structure response
    media = cloudkey.media.info(id=a_media_id)
    print media['id']

    # List of structures response
    media_list = cloudkey.media.list()
    for media in media_list:
        print media['id']

Local methods
=============

Additional local methods are exposed by the CloudKey class. They are not documented in the API
reference and provided as helpers to ease the Dailymotion Cloud API integration.

`file.upload_file(path)`
------------------------

This method manages files uploads to the Dailymotion Cloud upload servers. Information pertinent
to the API media creation processus (especially the media_set_asset method) will be returned as
a `dict`.

Arguments:

- 'path': (required) the path of the uploaded file.

Example:

    # source asset upload example
    file  = cloudkey.file.upload_file('path/to/video.mov')
    media = cloudkey.media.create()
    cloudkey.media.set_asset(id=media['id'], preset='source', url=file['url'])

`media.get_stream_url(id)`
--------------------------

This method returns a signed URL to the Dalymotion Cloud `mediastream` component (see the API refernce
for details). The generated URL is perishable, and access is granted based on the provided security level
bitmask.

Arguments:

- `id`: (required) the media id.
- `format`: the component output format (default is `'swf'` and currently is the only available format).
- `seclevel`: the security level bitmask (default is `SecLevel.NONE`, see below for details).
- `expires`: the UNIX epoch expiration time (default is `None`).

The following arguments may be required if the `SecLevel.DELEGATE` option is not specified in the seclevel
parameter, depending on the other options. This is not recommanded as it would probably lead to spurious
access denials, mainly due to GeoIP databases discrepancies.

- `asnum`: the client's autonomous system number (default is `None`).
- `ip`: the client's IP adress (default is `None`).
- `useragent`: the client's HTTP User-Agent header (default is `None`).

Example:

    // Create a media stream URL limited only to the AS of the end-user and valid for 1 hour
    url = cloudkey.media.get_stream_url(id=media['id'], seclevel=SecLevel.DELEGATE | SecLevel.ASNUM, expires=time() + 3600)

Security level options
======================

The security level defines the mechanism used by the Dailymotion Cloud architecture to ensure a mediastream
URL access will be limited to a single user or a group of users. The different (combinable) options are:

- `SecLevel.NONE`: the URL access is granted to everyone.

- `SecLevel.ASNUM`: the URL access is granted to the specified AS number only. AS numbers stands for 'Autonomous
   System number' and roughly map groups of IP to telcos and large organizations on the Internet (each ISP has its
   own AS number for instance, Dailyotion's AS number is AS41690).

- `SecLevel.IP`: the URL access is granted to the specified IP address only. This option may lead to spurious
   access denials as some users are load-balanced behind multiple proxies when accessing the Internet (this is
   mostly the case with ISPs and large organizations).

- `SecLevel.USERAGENT`: the URL access is granted to users sending the specified User-Agent HTTP header only.

- `SecLevel.DELEGATE`: the ASNUM, IP and User-Agent values are to be gathered at the server side during the
  first URL access and don't need to be specified at the client side beforehand (this is the recommanded
  approach as it will ensure a 100%-accurate ASNUM recognition).

- `SecLevel.USEONCE`: the URL access is granted once only (using this option will probably prevent seeking from
   working correctly).

For more information, please refer to the Dailymotion Cloud streams security documentation.

Exceptions
==========

The Dailymotion Cloud API methods may throw exceptions when errors occur, and they should be catched in your
code. The available exceptions are:

- `cloudkey.ApiException:` an unexpected API response occured.

- `cloudkey.InvalidNamespace:` an invalid namespace was used.

- `cloudkey.InvalidMethod:` an invalid method was called.

- `cloudkey.NotFound:` an action was requested on an invalid item.

- `cloudkey.MissingArgument:` a mandatory parameter was missing from a method call.

- `cloudkey.InvalidArgument:` an invalid parameter was specified in a method call.

- `cloudkey.AuthorizationRequired:` an authenticated method was call but no authentication information was provided.

- `cloudkey.AuthenticationFailed:` invalid authentication information was provided.
