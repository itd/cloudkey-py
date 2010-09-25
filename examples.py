#!/bin/env python

BASE_URL=None
USER_ID=None
API_KEY=None

try:
    from local_config import *
except ImportError:
    pass

if not USER_ID: USER_ID = raw_input('User ID: ')
if not API_KEY: API_KEY = raw_input('API Key: ')

import time, sys

from cloudkey import CloudKey

# We connect to the api with our login/password
cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)

#
# Adding media
#
# We upload one of our video

# We can have a callback to see the progress of the upload
#def my_upload_cb(name, progress, finished):
#    print '%s %s %s' % (name, progress, finished)
#
#media_info = cloudkey.media.upload('.fixtures/video.3gp', my_upload_cb)
media_info = cloudkey.file.upload_file(file='.fixtures/video.3gp')

# We create a new media
media_id = cloudkey.media.create()['id']

# We set a metadata 'title'
media_title = media_info['name'].replace('_', ' ')
cloudkey.media.set_meta(id=media_id, meta={'title': media_title})

# We set the video that we just uploaded as the source of our media
media_url = media_info['url']
cloudkey.media.set_assets(id=media_id, assets=[{'name': 'source', 'url': media_url}])

# This function retrieve an asset to check it's status and block until it's ready or failed
def wait_for_asset(media_id, asset_name):
    while True:
        asset = cloudkey.media.get_assets(id=media_id, assets_names=[asset_name])[asset_name]
        if asset['status'] != 'ready':
            if asset['status'] == 'error':
                print 'Asset couldn\'t be downloaded!'
                return False
            print '%s not ready: %s' % (asset_name, asset['status'])
            time.sleep(5)
            continue
        print '%s ready' % asset_name
        return True

# We wait until our source is ready
#wait_for_asset(media_id, 'source')

# We encode our source in two preset and wait for them
cloudkey.media.set_assets(id=media_id, assets=[{'name': 'flv_h263_mp3'}, {'name': 'mp4_h264_aac'}])

wait_for_asset(media_id, 'flv_h263_mp3')
wait_for_asset(media_id, 'mp4_h264_aac')

# There is a quicker way to publish a video
# we use avdanced feature of the create method to set some meta and encode the media in 2 presets
media_ = cloudkey.media.create(url=media_url, assets_names=['flv_h263_mp3', 'mp4_h264_aac'], meta={'title' : media_title, 'author' : 'John Doe' })

# we get the media id
media_id =  media_['id']

#
# Playing media
#
# You can retrieve the URL of a specific preset, this is the file
wait_for_asset(media_id, 'flv_h263_mp3')
print cloudkey.media.info(id=media_id, fields=['assets.flv_h263_mp3.stream_url'])

# you can retrieve the embed URL
print cloudkey.media.info(id=media_id, fields=['assets.flv_h263_mp3.embed_url'])

#
# Listing media
#
# We list the assets of the media we just uploaded
print cloudkey.media.get_assets(id=media_id)

# Print some info about our media
for m in cloudkey.media.list(fields=['id', 'meta.title', 'assets.flv_h263_mp3.stream_url', 'created'])['list']:
    print m

#
# Deleting media
#
# We delete the medias that have their source asset in error status
for m in cloudkey.media.list(fields=['id'])['list']:
    cloudkey.media.delete(id=m['id'])

