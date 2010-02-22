#!/bin/env python

import time, sys

from dcapi.media import Media

# We connect to the api with our login/password
media = Media('sebest', 'sebest', 'http://dk_api.sebest.dev.dailymotion.com')

# We upload one of our video

# We can have a callback to see the progress of the upload
#def my_upload_cb(name, progress, finished):
#    print '%s %s %s' % (name, progress, finished)
#
#media_info = media.upload('my_funny_video.3gp', my_upload_cb)
media_info = media.upload('my_funny_video.3gp')

# We create a new media
media_id = media.create()['id']

# We set a metadata 'title'
media_title = media_info['name'].replace('_', ' ')
media.set_meta(id=media_id, key='title', value=media_title)

# We set the video that we just uploaded as the source of our media
media_url = media_info['url']
media.set_asset(id=media_id, preset='source', url=media_url)

# This function retrieve an asset to check it's status and block until it's ready or failed
def wait_for_asset(media_id, asset_name):
    while True:
        asset = media.get_asset(id=media_id, preset=asset_name)
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
media.process_asset(id=media_id, preset='flv_h263_mp3')
media.process_asset(id=media_id, preset='mp4_h264_aac')

wait_for_asset(media_id, 'flv_h263_mp3')
wait_for_asset(media_id, 'mp4_h264_aac')
#sys.exit(0)
# We list the assets of the media we just uploaded
print media.list_asset(id=media_id)

# Print the media info of the assets that are ready for web streaming
for m in media.list(filter={'assets.flv_h263_mp3.status' : 'ready'}):
    print media.info(id=m['id'])

# we display the title and the status of the mp4 asset for medias that have their source in ready status
for m in media.list(fields=['assets.mp4_h264_aac.status', 'meta.title'], filter={'assets.source.status' : 'ready'}):
    print m

# We delete the medias that have their source asset in error status
for m in media.list(filter={'assets.source.status' : 'error'}):
    media.delete(id=m['id'])
