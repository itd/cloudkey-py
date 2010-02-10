#import time

from dkapi import DkAPI

def my_cb(name, progress, finished):
    print '%s %s %s' % (name, progress, finished)

c = DkAPI('sebest', 'sebest', 'dk_api.sebest.dev.dailymotion.com')
print c.media_upload('/home/sebest/Videos/i_am_legend-tlr2_1080p.mov')

#result = c.media_create()
#print c.media_asset_set(id=result['id'], preset='source', url='http://isidev-01-01.dev.dailymotion.com/video/695/203/11302596:source.mov')
#while True:
#    res = c.media_asset_process(id=result['id'], preset='flv_h263_mp3')
#    if res == 'Asset processing':
#        print 'ok'
#        break
#    else:
#        print 'sleeping'
#        time.sleep(5)
#
#
#print result
#print c.media_delete(id=result['id'])
#
#result = c.media_create()
#result = c.media_create()
#result = c.media_create()
#
#print c.media_meta_set(id=result['id'], key='title', value='mon super titre')
#
#c.media_asset_set(id='4b6b0c1a1b5d4237bf000007', preset='source', url='http://isidev-01-01.dev.dailymotion.com/video/695/203/11302596:source.mov')
#print c.media_asset_process(id='4b6b0c1a1b5d4237bf000007', preset='flv_h263_mp3')
#print c.media_asset_process(id='4b6b0c1a1b5d4237bf000007', preset='flv_h263_mp3')
#print c.media_asset_process(id='4b6b0c1a1b5d4237bf000007', preset='flv_h263_mp3')
#fields = json.dumps(['assets.source.status', 'metas'])
#filter = json.dumps({'assets.source.status' : 'ready'})
#for i in c.media_list(filter=filter, fields=fields):
#print c.media_info(id='4b6b24a31b5d421249000009')
#
#for i in c.media_list():
#    print i
#
#print c.media_asset_list(id='4b6b0c1a1b5d4237bf000007')
