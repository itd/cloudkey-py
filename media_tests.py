import unittest
import os, time

from cloudkey.media import *

class MediaTestBase(unittest.TestCase):

    def setUp(self):
        self.media = Media('sebest', 'sebest', 'http://dc_api.sebest.dev.dailymotion.com')
        self.media.reset()

    def tearDown(self):
        pass

    def test_media_create(self):
        media = self.media.create()

        self.assertEqual(type(media), dict)
        self.assertEqual(media.keys(), ['id'])
        self.assertEqual(len(media['id']), 24)

    def test_media_info(self):
        media = self.media.create()
        res = self.media.info(id=media['id'])

        self.assertEqual(type(res), dict)
        self.assertEqual(res.keys(), ['id'])
        self.assertEqual(len(res['id']), 24)

# TODO       self.assertRaises(InvalidArgument,  self.media.info, id=media['id'][:-2])
        self.assertRaises(NotFound,  self.media.info, id=media['id'][:-2])

    def test_media_delete(self):
        media = self.media.create()
        res = self.media.delete(id=media['id'])

        self.assertEqual(res, None)

        self.assertRaises(NotFound, self.media.info, id=media['id'])

        self.assertRaises(NotFound, self.media.delete, id=media['id'])

        self.assertRaises(NotFound, self.media.delete, id='1'+media['id'][1:])

    def test_media_set_meta(self):
        media = self.media.create()

        res = self.media.set_meta(id=media['id'], key='mykey', value='value')
        self.assertEqual(res, None)

        self.assertRaises(MissingArgument, self.media.set_meta, id=media['id'], key='mykey')
        self.assertRaises(MissingArgument, self.media.set_meta, id=media['id'], value='myvalue')
        self.assertRaises(MissingArgument, self.media.set_meta, id=media['id'])

        # update value
        res = self.media.set_meta(id=media['id'], key='mykey', value='value')
        self.assertEqual(res, None)

        # unicode key/value
        res = self.media.set_meta(id=media['id'], key=u'u_mykey', value=u'u_value')
        self.assertEqual(res, None)

        self.assertRaises(NotFound, self.media.set_meta, id='1'+media['id'][1:], key='theky', value='thevalue')

    def test_media_get_meta(self):
        media = self.media.create()
        self.media.set_meta(id=media['id'], key='mykey', value='value')

        res = self.media.get_meta(id=media['id'], key='mykey')
        self.assertEqual(type(res), dict)
        self.assertEqual(res.keys(), ['value'])
        self.assertEqual(res['value'], 'value')

        self.assertRaises(NotFound, self.media.get_meta, id=media['id'], key='invalid_key')
        self.assertRaises(NotFound, self.media.get_meta, id=media['id'], key=[])

        # update value
        self.media.set_meta(id=media['id'], key='mykey', value='new_value')
        res = self.media.get_meta(id=media['id'], key='mykey')
        self.assertEqual(type(res), dict)
        self.assertEqual(res.keys(), ['value'])
        self.assertEqual(res['value'], 'new_value')

        # unicode key/value
        self.media.set_meta(id=media['id'], key=u'u_mykey', value=u'u_value')
        res = self.media.get_meta(id=media['id'], key=u'u_mykey')
        self.assertEqual(type(res), dict)
        self.assertEqual(res.keys(), ['value'])
        self.assertEqual(res['value'], u'u_value')

    def test_media_remove_meta(self):
        media = self.media.create()
        self.media.set_meta(id=media['id'], key='mykey', value='value')

        res = self.media.remove_meta(id=media['id'], key='mykey')
        self.assertEqual(res, None)
        
        self.assertRaises(NotFound, self.media.remove_meta, id=media['id'], key='mykey')

        self.assertRaises(NotFound, self.media.get_meta, id=media['id'], key='mykey')

    def test_media_list_meta(self):
        media = self.media.create()
        res = self.media.list_meta(id=media['id'])
        self.assertEqual(type(res), dict)
        self.assertEqual(len(res.keys()), 0)

        for i in range(10):
            self.media.set_meta(id=media['id'], key='mykey-%d' % i, value='value-%d' % i)

        res = self.media.list_meta(id=media['id'])
        self.assertEqual(type(res), dict)
        self.assertEqual(len(res.keys()), 10)

        for i in range(10):
            self.assertEqual(res['mykey-%d' %i], 'value-%d' % i)

    def test_media_list(self):
        res = self.media.list()
        self.assertEqual(res, [])

        medias = []
        for i in range(25):
            medias.append(self.media.create())
        res = self.media.list()
        self.assertEqual(res, medias)

        res = self.media.list(page=1)
        self.assertEqual(res, medias[:10])

        res = self.media.list(page=2)
        self.assertEqual(res, medias[10:20])

        res = self.media.list(page=2, count=6)
        self.assertEqual(res, medias[6:12])

        x = 0
        for media in medias:
            x += 1
            if x % 2:
                for i in range(5):
                    self.media.set_meta(id=media['id'], key='mykey-%d' % i, value='value-%d' % i)
            else:
                self.media.set_meta(id=media['id'], key='mykey-1', value='42')

        fields = ['meta.mykey-2', 'meta.mykey-3']
        filter = {'meta.mykey-1' : 'value-1'}
        res = self.media.list(fields=fields, filter=filter)
        self.assertEqual(len(res), 13)

        for i in res:
            self.assertEqual(len(i.keys()), 2)
            self.assertEqual(i['meta'].get('mykey-2'), 'value-2')
            self.assertEqual(i['meta'].get('mykey-3'), 'value-3')
            self.assertEqual(i['meta'].get('mykey-1'), None)

        filter = {'meta.mykey-1' : '42'}
        res = self.media.list(filter=filter)
        self.assertEqual(len(res), 12)
        for i in res:
            self.assertEqual(len(i.keys()), 1)
            self.assertEqual(i.keys(), ['id'])

    def test_media_upload(self):
        media_info = self.media.upload('my_funny_video.3gp')
        self.assertEqual(media_info['size'], 92545)
        self.assertEqual(media_info['name'], 'my_funny_video')
        self.assertEqual('url' in media_info.keys(), True)

    def test_media_set_asset(self):
        media_info = self.media.upload('my_funny_video.3gp')
        media_url = media_info['url']

        media = self.media.create()
        res = self.media.set_asset(id=media['id'], preset='source', url=media_url)
        self.assertEqual(res, None)

    def wait_for_asset(self, media_id, asset_name):
        while True:
            asset = self.media.get_asset(id=media_id, preset=asset_name)
            if asset['status'] != 'ready':
                if asset['status'] == 'error':
                    #print 'Asset couldn\'t be downloaded!'
                    return False
                #print '%s not ready: %s' % (asset_name, asset['status'])
                time.sleep(5)
                continue
            #print '%s ready' % asset_name
            return True

    def test_media_get_asset(self):
        media_info = self.media.upload('my_funny_video.3gp')
        media_url = media_info['url']

        media = self.media.create()
        res = self.media.set_asset(id=media['id'], preset='source', url=media_url)
        
        res = self.media.get_asset(id= media['id'], preset='source')
        self.assertEqual('status' in res.keys(), True)
        self.assertEqual(res['status'] in ('pending', 'processing'), True)

        res = self.wait_for_asset(media['id'], 'source')
        self.assertEqual(res, True)
        res = self.media.get_asset(id=media['id'], preset='source')
        self.assertEqual('status' in res.keys(), True)
        self.assertEqual(res['status'], 'ready')


    def wait_for_remove_asset(self, media_id, asset_name, timeout=10):
        for i in range(timeout):
            try:
                self.media.get_asset(id=media_id, preset=asset_name)
            except NotFound, e:
                return True
            time.sleep(1)
        else:
            return False

    def test_media_remove_asset(self):
        media_info = self.media.upload('my_funny_video.3gp')
        media_url = media_info['url']

        media = self.media.create()
        res = self.media.set_asset(id=media['id'], preset='source', url=media_url)
        res = self.wait_for_asset(media['id'], 'source')
        self.assertEqual(res, True)

        res = self.media.remove_asset(id=media['id'], preset='source')
        self.assertEqual(res, None)
        res = self.wait_for_remove_asset(media['id'], 'source', 20)
        self.assertEqual(res, True)

        self.media.set_asset(id=media['id'], preset='source', url=media_url)
        res = self.media.remove_asset(id=media['id'], preset='source')
        self.assertEqual(res, None)

        res = self.wait_for_remove_asset(media['id'], 'source')
        self.assertEqual(res, True)
        res = self.wait_for_remove_asset(media['id'], 'source')
        self.assertEqual(res, True)
        self.assertRaises(NotFound, self.media.get_asset, id=media['id'], preset='source')

    def test_media_process_asset(self):
        media_info = self.media.upload('my_funny_video.3gp')
        media_url = media_info['url']

        media = self.media.create()
        res = self.media.set_asset(id=media['id'], preset='source', url=media_url)
        res = self.media.process_asset(id=media['id'], preset='flv_h263_mp3')
        self.assertEqual(res, None)
        res = self.media.process_asset(id=media['id'], preset='mp4_h264_aac')
        self.assertEqual(res, None)
        res = self.media.get_asset(id= media['id'], preset='flv_h263_mp3')
        self.assertEqual(res['status'], 'pending')
        res = self.media.get_asset(id= media['id'], preset='mp4_h264_aac')
        self.assertEqual(res['status'], 'pending')
        res = self.wait_for_asset(media['id'], 'flv_h263_mp3')
        res = self.wait_for_asset(media['id'], 'mp4_h264_aac')
        res = self.media.get_asset(id= media['id'], preset='flv_h263_mp3')
        self.assertEqual(res['status'], 'ready')
        self.assertEqual(res.keys() == ['status', 'duration', 'filesize'], True)
        res = self.media.get_asset(id= media['id'], preset='mp4_h264_aac')
        self.assertEqual(res['status'], 'ready')
        self.assertEqual(res.keys() == ['status', 'duration', 'filesize'], True)
        
#        my_broken_video.avi

if __name__ == '__main__':
    unittest.main()
