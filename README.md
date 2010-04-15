The Dailymotion Cloud API Python binding exposes all API methods described the API reference. A
master class named `CloudKey` exposes all namespaces through object attributes. For
instance, to call the `count` method from the `media` namespace, the code
would be as follow:

    cloudkey = CloudKey(username, password)
    result = cloudkey.media.count()

To pass arguments to method, an named arguments are passed to the called method:

    media = cloudkey.media.info(id: a_media_id)

When method returns something, the result is either an `dict` when result is
a structure or a `list` of `dict`s when result is a list:

    # Simple structure response type
    media = cloudkey.media.info(id=a_media_id)
    print media['id']

    # List of structures response type
    media_list = cloudkey.media.list()
    for media in media_list:
        print media['id']

There is one additional method not documented in the API reference which is an helper to upload
media files. This helper is available in the `file` namespace and is named `upload_file`. This
method takes a path to a file as a first argument and returns uploaded file information like its URL
which can be provided to the `media.set_asset` method:

    file = cloudkey.file.upload_file('path/to/video.mov')
    media = cloudkey.media.create()
    cloudkey.media.set_asset(id=media['id'], preset='source', url=file['url'])

Methods can throw exceptions when errors occurs, be prepared to handle them. Here is a list of
exception which could be thrown:

- `cloudkey.ApiException:` When unexpected API response occurs
- `cloudkey.InvalidNamespace:` When an invalid namespace is used
- `cloudkey.InvalidMethod:` When a not existing method is called
- `cloudkey.NotFound:` When action is requested on an not existing item
- `cloudkey.MissingArgument:` When a method is called with a missing mandatory parameter
- `cloudkey.InvalidArgument:` When a method is called with a invalid parameter
- `cloudkey.AuthorizationRequired:` When an authenticated method is call with not authentication information
- `cloudkey.AuthenticationFailed:` When authentication information is invalidg
