#import time

import time
import sys

from dkapi import DkAPI

def my_cb(name, progress, finished):
    print '%s %s %s' % (name, progress, finished)

c = DkAPI('sebest', 'sebest', 'dk_api.sebest.dev.dailymotion.com')

# We upload one of our video
media_info = c.media_upload('/home/sebest/Videos/i_am_legend-tlr2_h1080p.mov')

# We create a new media
media_id = c.media_create()['id']

# We set a metadata 'title'
media_title = media_info['name'].replace('_', ' ')
c.media_meta_set(id=media_id, key='title', value=media_title)

# We set the video that we just uploaded as the source of our media
media_url = media_info['url']
c.media_asset_set(id=media_id, preset='source', url=media_url)

# We wait until our source is ready
while True:
    asset = c.media_asset_get(id=media_id, preset='source')
    if asset['status'] != 'ready':
        if asset['status'] == 'error':
            print 'Source couldn t be downloaded!'
            sys.exit(0)
        print 'Source not ready: %s' % asset['status']
        time.sleep(5)
        continue
    print 'Source ready'
    break

# We encode our source in two preset
c.media_asset_process(id=media_id, preset='flv_h263_mp3')
c.media_asset_process(id=media_id, preset='mp4_h264_aac')

# We list our assets
print c.media_asset_list(id=media_id)


#print c.media_delete(id=result['id'])
#print c.media_info(id='4b6b24a31b5d421249000009')
#
#fields = json.dumps(['assets.source.status', 'meta'])
#filter = json.dumps({'assets.source.status' : 'ready'})
#for i in c.media_list(filter=filter, fields=fields):
#    print i
