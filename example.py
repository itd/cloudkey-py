#!/bin/env python

import time

from dkapi import DkAPI

# We connect to the api with our login/password
c = DkAPI('sebest', 'sebest', 'dk_api.sebest.dev.dailymotion.com')

# We upload one of our video

# We can have a callback to see the progress of the upload
#def my_upload_cb(name, progress, finished):
#    print '%s %s %s' % (name, progress, finished)
#
#media_info = c.media_upload('my_funny_video.3gp', my_upload_cb)
media_info = c.media_upload('my_funny_video.3gp')

# We create a new media
media_id = c.media_create()['id']

# We set a metadata 'title'
media_title = media_info['name'].replace('_', ' ')
c.media_meta_set(id=media_id, key='title', value=media_title)

# We set the video that we just uploaded as the source of our media
media_url = media_info['url']
c.media_asset_set(id=media_id, preset='source', url=media_url)

# This function retrieve an asset to check it's status and block until it's ready or failed
def wait_for_asset(asset_name):
    while True:
        asset = c.media_asset_get(id=media_id, preset=asset_name)
        if asset['status'] != 'ready':
            if asset['status'] == 'error':
                print 'Asset couldn\'t be downloaded!'
                return False
            print '%s not ready: %s' % (asset['status'], asset_name)
            time.sleep(5)
            continue
        print '%s ready' % asset_name
        return True

# We wait until our source is ready
wait_for_asset('source')

# We encode our source in two preset and wait for them
c.media_asset_process(id=media_id, preset='flv_h263_mp3')
c.media_asset_process(id=media_id, preset='mp4_h264_aac')

wait_for_asset('flv_h263_mp3')
wait_for_asset('mp4_h264_aac')

# We list the assets of the media we just uploaded
print c.media_asset_list(id=media_id)

# Print the media info of the assets that are ready for web streaming
for media in c.media_list(filter={'assets.flv_h263_mp3.status' : 'ready'}):
    print c.media_info(id=media['id'])

# we display the title and the status of the mp4 asset for medias that have their source in ready status
for media in c.media_list(fields=['assets.mp4_h264_aac.status', 'meta.title'], filter={'assets.source.status' : 'ready'}):
    print media

# We delete the medias that have their source asset in error status
for media in c.media_list(filter={'assets.source.status' : 'error'}):
    c.media_delete(id=media['id'])
