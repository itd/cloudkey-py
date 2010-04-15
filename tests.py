USERNAME='test'
PASSWORD='qwsxdcfv'
BASE_URL='http://api.dmcloud.net'

import unittest
import os, time

from cloudkey import CloudKey, NotFound, InvalidArgument, MissingArgument, AuthorizationRequired, AuthenticationFailed

class MediaTestDelete(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_delete(self):
        media = self.cloudkey.media.create()
        res = self.cloudkey.media.delete(id=media['id'])

        self.assertEqual(res, None)

        self.assertRaises(NotFound, self.cloudkey.media.info, id=media['id'])

    def test_media_not_found(self):
        self.assertRaises(NotFound, self.cloudkey.media.delete, id='1b87186c84e1b015a0000000')

    def test_invalid_media_id(self):
        self.assertRaises(InvalidArgument, self.cloudkey.media.delete, id='b87186c84e1b015a0000000')

class MediaTestInfo(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_info(self):
        media = self.cloudkey.media.create()
        res = self.cloudkey.media.info(id=media['id'])

        self.assertEqual(type(res), dict)
        self.assertEqual(set(res.keys()), set([u'asset_statuses', u'meta', u'id', u'assets']))
        self.assertEqual(len(res['id']), 24)

    def test_media_not_found(self):
        self.assertRaises(NotFound, self.cloudkey.media.info, id='1b87186c84e1b015a0000000')

    def test_invalid_media_id(self):
        self.assertRaises(InvalidArgument, self.cloudkey.media.info, id='b87186c84e1b015a0000000')

class MediaTestCreate(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_create(self):
        media = self.cloudkey.media.create()

        self.assertEqual(type(media), dict)
        self.assertEqual(media.keys(), ['id'])
        self.assertEqual(len(media['id']), 24)

class MediaTestMeta(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_set_get(self):
        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_meta(id=media['id'], key='mykey', value='my_value')
        self.assertEqual(res, None)

        res = self.cloudkey.media.get_meta(id=media['id'], key='mykey')
        self.assertEqual(type(res), dict)
        self.assertEqual(res.keys(), ['value'])
        self.assertEqual(res['value'], 'my_value')

    def test_media_not_found(self):
        self.assertRaises(NotFound, self.cloudkey.media.set_meta,
                          id='1b87186c84e1b015a0000000', key='mykey', value='my_value')

    def test_invalid_media_id(self):
        self.assertRaises(InvalidArgument, self.cloudkey.media.set_meta,
                          id='b87186c84e1b015a0000000', key='mykey', value='my_value')

    def test_missing_argument(self):
        media = self.cloudkey.media.create()

        self.assertRaises(MissingArgument, self.cloudkey.media.set_meta, id=media['id'], key='mykey')
        self.assertRaises(MissingArgument, self.cloudkey.media.set_meta, id=media['id'], value='myvalue')
        self.assertRaises(MissingArgument, self.cloudkey.media.set_meta, id=media['id'])
        self.assertRaises(MissingArgument, self.cloudkey.media.get_meta, id=media['id'])
        self.assertRaises(MissingArgument, self.cloudkey.media.remove_meta, id=media['id'])

    def test_set_meta_update(self):
        media = self.cloudkey.media.create()

        res = self.cloudkey.media.set_meta(id=media['id'], key='mykey', value='value')
        self.assertEqual(res, None)

        res = self.cloudkey.media.set_meta(id=media['id'], key='mykey', value='my_new_value')
        self.assertEqual(res, None)

        res = self.cloudkey.media.get_meta(id=media['id'], key='mykey')
        self.assertEqual(type(res), dict)
        self.assertEqual(res.keys(), ['value'])
        self.assertEqual(res['value'], 'my_new_value')

    def test_set_meta_unicode(self):
        media = self.cloudkey.media.create()

        res = self.cloudkey.media.set_meta(id=media['id'], key=u'u_mykey', value=u'u_value')
        self.assertEqual(res, None)

        res = self.cloudkey.media.get_meta(id=media['id'], key=u'u_mykey')
        self.assertEqual(type(res), dict)
        self.assertEqual(res.keys(), ['value'])
        self.assertEqual(res['value'], 'u_value')

    def test_meta_not_found(self):
        media = self.cloudkey.media.create()

        self.assertRaises(NotFound, self.cloudkey.media.get_meta, id=media['id'], key='invalid_key')
        self.assertRaises(NotFound, self.cloudkey.media.get_meta, id=media['id'], key=[])
        self.assertRaises(NotFound, self.cloudkey.media.get_meta, id=media['id'], key=100)

    def test_invalid_key(self):
        media = self.cloudkey.media.create()

        #self.cloudkey.media.get_meta(id=media['id'], key=100)

    def test_list(self):
        media = self.cloudkey.media.create()

        res = self.cloudkey.media.list_meta(id=media['id'])
        self.assertEqual(type(res), dict)
        self.assertEqual(len(res), 0)

        for i in range(10):
            self.cloudkey.media.set_meta(id=media['id'], key='mykey-%d' % i, value='value-%d' % i)

        res = self.cloudkey.media.list_meta(id=media['id'])
        self.assertEqual(type(res), dict)
        self.assertEqual(len(res.keys()), 10)

        for i in range(10):
            self.assertEqual(res['mykey-%d' %i], 'value-%d' % i)

    def test_remove(self):
        media = self.cloudkey.media.create()
        self.cloudkey.media.set_meta(id=media['id'], key='mykey', value='value')

        res = self.cloudkey.media.remove_meta(id=media['id'], key='mykey')
        self.assertEqual(res, None)

        self.assertRaises(NotFound, self.cloudkey.media.remove_meta, id=media['id'], key='mykey')
        self.assertRaises(NotFound, self.cloudkey.media.get_meta, id=media['id'], key='mykey')

class MediaTestAssetUrl(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_media_get_asset_url_preview(self):
        preset = 'jpeg_thumbnail_small'

        media_id = self.cloudkey.media.create()['id']
        url = self.cloudkey.media.get_asset_url(id=media_id, preset=preset)
        import urlparse
        parsed = urlparse.urlparse(url)
        #self.assertEqual(parsed.netloc, 'static.dmcloud.net')
        spath = parsed.path.split('/')
        #self.assertEqual(len(spath), 4)
        #self.assertEqual(spath[3].split('.')[0], preset)

    def test_media_get_asset_url_video(self):
        preset = 'mp4_h264_aac'

        media_id = self.cloudkey.media.create()['id']
        url = self.cloudkey.media.get_asset_url(id=media_id, preset=preset)
        import urlparse
        parsed = urlparse.urlparse(url)
        #self.assertEqual(parsed.netloc, 'cdndirector.dmcloud.net')
        spath = parsed.path.split('/')
        #self.assertEqual(len(spath), 5)
        #self.assertEqual(spath[4].split('.')[0], preset)
        #self.assertEqual(spath[1], 'route')

class MediaTestAssetStatus(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def wait_for_asset(self, media_id, asset_name, wait=60):
        for i in range(wait):
            asset = self.cloudkey.media.get_asset(id=media_id, preset=asset_name)
            #print asset
            if asset['status'] != 'ready':
                if asset['status'] == 'error':
                    #print 'Asset couldn\'t be downloaded!'
                    return False
                #print '%s not ready: %s' % (asset_name, asset['status'])
                time.sleep(1)
                continue
            #print '%s ready' % asset_name
            return True
        raise Exception('timeout exceeded')

    def wait_for_remove_asset(self, media_id, asset_name, timeout=10):
        for i in range(timeout):
            try:
                self.cloudkey.media.get_asset(id=media_id, preset=asset_name)
            except NotFound, e:
                return True
            time.sleep(1)
        else:
            raise Exception('timeout exceeded')

    def test_asset_status_ready(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        preset = 'source'

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media['id'], preset=preset, url=media_url)

        res = self.cloudkey.media.get_asset(id= media['id'], preset=preset)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.' + res['status'] : preset })

        #print 'ready %s' % self.cloudkey.media.list(filter={ 'asset_statuses.ready' : preset })
        #print 'error %s' % self.cloudkey.media.list(filter={ 'asset_statuses.error' : preset })
        #print 'pending %s' % self.cloudkey.media.list(filter={ 'asset_statuses.pending' : preset })
        #print 'processing %s' % self.cloudkey.media.list(filter={ 'asset_statuses.processing' : preset })

        self.assertEqual(res[0]['id'], media['id'])

        res = self.wait_for_asset(media['id'], preset)
        self.assertEqual(res, True)

        res = self.cloudkey.media.list(filter={ 'asset_statuses.pending' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.processing' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.ready' : preset })
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['id'], media['id'])

        preset='flv_h263_mp3'
        res = self.cloudkey.media.process_asset(id=media['id'], preset=preset)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.pending' : preset })
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['id'], media['id'])

        res = self.wait_for_asset(media['id'], preset)
        self.assertEqual(res, True)

        res = self.cloudkey.media.list(filter={ 'asset_statuses.pending' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.processing' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.ready' : preset })
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['id'], media['id'])

        res = self.cloudkey.media.remove_asset(id=media['id'], preset=preset)
        res = self.wait_for_remove_asset(media['id'], preset, 20)
        self.assertEqual(res, True)

        res = self.cloudkey.media.list(filter={ 'asset_statuses.pending' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.processing' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.ready' : preset })
        self.assertEqual(len(res), 0)

    def test_asset_status_error(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/broken_video.avi')
        media_url = media_info['url']

        preset = 'source'

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media['id'], preset=preset, url=media_url)
        res = self.wait_for_asset(media['id'], preset)
        self.assertEqual(res, True)

        preset='flv_h263_mp3'
        res = self.cloudkey.media.process_asset(id=media['id'], preset=preset)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.pending' : preset })
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['id'], media['id'])

        res = self.wait_for_asset(media['id'], preset)
        self.assertEqual(res, False)

        res = self.cloudkey.media.list(filter={ 'asset_statuses.pending' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.processing' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.ready' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.error' : preset })
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['id'], media['id'])

        res = self.cloudkey.media.remove_asset(id=media['id'], preset=preset)

        res = self.cloudkey.media.list(filter={ 'asset_statuses.pending' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.processing' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.ready' : preset })
        self.assertEqual(len(res), 0)
        res = self.cloudkey.media.list(filter={ 'asset_statuses.error' : preset })
        self.assertEqual(len(res), 0)


class MediaTestAsset(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_media_set_asset(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media['id'], preset='source', url=media_url)
        self.assertEqual(res, None)

    def wait_for_asset(self, media_id, asset_name, wait=60):
        for i in range(wait):
            asset = self.cloudkey.media.get_asset(id=media_id, preset=asset_name)
            #print asset
            if asset['status'] != 'ready':
                if asset['status'] == 'error':
                    #print 'Asset couldn\'t be downloaded!'
                    return False
                #print '%s not ready: %s' % (asset_name, asset['status'])
                time.sleep(1)
                continue
            #print '%s ready' % asset_name
            return True
        raise Exception('timeout exceeded')

    def test_media_get_asset(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media['id'], preset='source', url=media_url)

        res = self.cloudkey.media.get_asset(id= media['id'], preset='source')
        self.assertEqual('status' in res.keys(), True)
        self.assertEqual(res['status'] in ('pending', 'processing'), True)

        res = self.wait_for_asset(media['id'], 'source')
        self.assertEqual(res, True)
        res = self.cloudkey.media.get_asset(id=media['id'], preset='source')
        self.assertEqual('status' in res.keys(), True)
        self.assertEqual(res['status'], 'ready')


    def wait_for_remove_asset(self, media_id, asset_name, timeout=10):
        for i in range(timeout):
            try:
                self.cloudkey.media.get_asset(id=media_id, preset=asset_name)
            except NotFound, e:
                return True
            time.sleep(1)
        else:
            raise Exception('timeout exceeded')

    def test_media_remove_asset(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media['id'], preset='source', url=media_url)
        res = self.wait_for_asset(media['id'], 'source')
        self.assertEqual(res, True)

        res = self.cloudkey.media.remove_asset(id=media['id'], preset='source')
        self.assertEqual(res, None)
        res = self.wait_for_remove_asset(media['id'], 'source', 20)
        self.assertEqual(res, True)

        self.cloudkey.media.set_asset(id=media['id'], preset='source', url=media_url)
        res = self.cloudkey.media.remove_asset(id=media['id'], preset='source')
        self.assertEqual(res, None)

        res = self.wait_for_remove_asset(media['id'], 'source')
        self.assertEqual(res, True)
        self.assertRaises(NotFound, self.cloudkey.media.get_asset, id=media['id'], preset='source')

    def test_media_process_asset(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media['id'], preset='source', url=media_url)
        res = self.cloudkey.media.process_asset(id=media['id'], preset='flv_h263_mp3')
        self.assertEqual(res, None)
        res = self.cloudkey.media.process_asset(id=media['id'], preset='mp4_h264_aac')
        self.assertEqual(res, None)
        res = self.cloudkey.media.get_asset(id= media['id'], preset='flv_h263_mp3')
        self.assertEqual(res['status'], 'pending')
        res = self.cloudkey.media.get_asset(id= media['id'], preset='mp4_h264_aac')
        self.assertEqual(res['status'], 'pending')
        res = self.wait_for_asset(media['id'], 'flv_h263_mp3')
        self.assertEqual(res, True)
        res = self.wait_for_asset(media['id'], 'mp4_h264_aac')
        self.assertEqual(res, True)
        res = self.cloudkey.media.get_asset(id= media['id'], preset='flv_h263_mp3')
        self.assertEqual(res['status'], 'ready')
        self.assertEqual(set(res.keys()), set(['status', 'duration', 'filesize']))
        res = self.cloudkey.media.get_asset(id= media['id'], preset='mp4_h264_aac')
        self.assertEqual(res['status'], 'ready')
        self.assertEqual(set(res.keys()), set(['status', 'duration', 'filesize']))

#        my_broken_video.avi

class MediaTestPublish(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_publish(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        presets = ['flv_h263_mp3', 'mp4_h264_aac', 'flv_h263_mp3_ld', 'jpeg_thumbnail_small', 'jpeg_thumbnail_medium', 'jpeg_thumbnail_large']

        media = self.cloudkey.media.publish(url=media_url, presets=presets)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media['id'], preset=preset)
            self.assertEqual(res['status'], 'pending')

        for preset in presets:
            res = self.wait_for_asset(media['id'], preset)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media['id'], preset=preset)
            self.assertEqual(res['status'], 'ready')
            self.assertEqual(set(res.keys()), set(['status', 'duration', 'filesize']))

    def test_publish_source_error(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/broken_video.avi')
        media_url = media_info['url']

        presets = ['flv_h263_mp3', 'mp4_h264_aac', 'flv_h263_mp3_ld']

        media = self.cloudkey.media.publish(url=media_url, presets=presets)

        for preset in presets:
            res = self.wait_for_asset(media['id'], preset)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media['id'], preset=preset)
            self.assertEqual(res['status'], 'error')
            self.assertEqual(res.keys(), ['status'])

    def test_publish_url_error(self):
        media_url = 'http://localhost/'

        presets = ['flv_h263_mp3', 'mp4_h264_aac', 'flv_h263_mp3_ld']

        media = self.cloudkey.media.publish(url=media_url, presets=presets)

        for preset in presets:
            res = self.wait_for_asset(media['id'], preset, 10)
            self.assertEqual(res, False)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media['id'], preset=preset)
            self.assertEqual(res['status'], 'error')
            self.assertEqual(res.keys(), ['status'])

    def wait_for_asset(self, media_id, asset_name, wait=60):
        for i in range(wait):
            asset = self.cloudkey.media.get_asset(id=media_id, preset=asset_name)
            if asset['status'] != 'ready':
                if asset['status'] == 'error':
                    #print 'Asset couldn\'t be downloaded!'
                    return False
                #print '%s not ready: %s' % (asset_name, asset['status'])
                time.sleep(1)
                continue
            #print '%s ready' % asset_name
            return True
        #print self.cloudkey.media.list_asset()
        raise Exception('timeout exceeded')


class MediaTestFileUpload(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_file_upload(self):
        # status url
        res = self.cloudkey.file.upload()
        self.assertEqual('url' in res.keys(), True)

    def test_file_upload_target(self):
        mytarget='http://www.example.com/myform'
        res = self.cloudkey.file.upload(target=mytarget)
        self.assertEqual('url' in res.keys(), True)
        import urlparse
        parsed = urlparse.urlparse(res['url'])
        myqs = urlparse.parse_qs(parsed.query)
        self.assertEqual(myqs.keys() , ['seal', 'uuid', 'target', ])
        self.assertEqual(myqs['target'][0] , mytarget)

    def test_media_upload(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        self.assertEqual(media_info['size'], 92545)
        self.assertEqual(media_info['name'], 'video')
        self.assertEqual('url' in media_info.keys(), True)

class MediaTestList(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_empty_list(self):
        res = self.cloudkey.media.list()
        self.assertEqual(res, [])

    def test_list(self):
        medias = []
        for i in range(25):
            medias.append({u'asset_statuses': {}, u'meta': {}, u'id': self.cloudkey.media.create()['id'], u'assets': {}})
        res = self.cloudkey.media.list()
        self.assertEqual(res, medias)

    def test_pagination(self):
        medias = []
        for i in range(25):
            medias.append({u'asset_statuses': {}, u'meta': {}, u'id': self.cloudkey.media.create()['id'], u'assets': {}})

        res = self.cloudkey.media.list(page=1)
        self.assertEqual(res, medias[:10])

        res = self.cloudkey.media.list(page=2)
        self.assertEqual(res, medias[10:20])

        res = self.cloudkey.media.list(page=2, count=6)
        self.assertEqual(res, medias[6:12])

    def test_invalid_filter(self):
        medias = []
        for i in range(5):
            medias.append(self.cloudkey.media.create())

        self.assertRaises(InvalidArgument, self.cloudkey.media.list,
                          filter = { '$where' : "this.a > 3" })

        self.assertRaises(InvalidArgument, self.cloudkey.media.list,
                          filter = "this.a > 3")

    def test_invalid_fields(self):
        medias = []
        for i in range(5):
            medias.append(self.cloudkey.media.create())

        self.assertRaises(InvalidArgument, self.cloudkey.media.list,
                          fields = "this.a")

    def test_invalid_sort(self):
        medias = []
        for i in range(5):
            medias.append(self.cloudkey.media.create())

        self.assertRaises(InvalidArgument, self.cloudkey.media.list,
                          fields = "this.a")

    def test_fields_filter(self):
        medias = []
        for i in range(25):
            medias.append(self.cloudkey.media.create())

        x = 0
        for media in medias:
            x += 1
            if x % 2:
                for i in range(5):
                    self.cloudkey.media.set_meta(id=media['id'], key='mykey-%d' % i, value='value-%d' % i)
            else:
                self.cloudkey.media.set_meta(id=media['id'], key='mykey-1', value='42')

        fields = ['meta.mykey-2', 'meta.mykey-3']
        filter = {'meta.mykey-1' : 'value-1'}
        res = self.cloudkey.media.list(fields=fields, filter=filter)
        self.assertEqual(len(res), 13)

        for i in res:
            self.assertEqual(len(i.keys()), 4)
            self.assertEqual(i['meta'].get('mykey-2'), 'value-2')
            self.assertEqual(i['meta'].get('mykey-3'), 'value-3')
            self.assertEqual(i['meta'].get('mykey-1'), None)

        filter = {'meta.mykey-1' : '42'}
        res = self.cloudkey.media.list(filter=filter)
        self.assertEqual(len(res), 12)
        for i in res:
            self.assertEqual(len(i.keys()), 4)
            self.assertEqual(set(i.keys()), set([u'asset_statuses', u'meta', u'id', u'assets']))


class MediaTestBase(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_media_create(self):
        media = self.cloudkey.media.create()

        self.assertEqual(type(media), dict)
        self.assertEqual(media.keys(), ['id'])
        self.assertEqual(len(media['id']), 24)


class MediaTestAuth(unittest.TestCase):

    def test_anonymous(self):
        cloudkey = CloudKey(None, None, BASE_URL)
        self.assertRaises(AuthorizationRequired, cloudkey.user.whoami)

    def test_normal_user(self):
        cloudkey = CloudKey('test', 'qwsxdcfv', BASE_URL)
        res = cloudkey.user.whoami()
        self.assertEqual(res['username'], 'test')

    def test_normal_user_su(self):
        cloudkey = CloudKey('test', 'qwsxdcfv', BASE_URL)
        cloudkey.act_as_user('sebest')
        res = cloudkey.user.whoami()
        self.assertEqual(res['username'], 'test')

    def test_super_user(self):
        cloudkey = CloudKey('root', 'qwsxdcfv', BASE_URL)
        res = cloudkey.user.whoami()
        self.assertEqual(res['username'], 'root')

    def test_super_user_su(self):
        cloudkey = CloudKey('root', 'qwsxdcfv', BASE_URL)
        cloudkey.act_as_user('sebest')
        res = cloudkey.user.whoami()
        self.assertEqual(res['username'], 'sebest')

    def test_super_user_su_wrong_user(self):
        cloudkey = CloudKey('root', 'test', BASE_URL)
        cloudkey.act_as_user('johndoe')
        self.assertRaises(AuthenticationFailed, cloudkey.user.whoami)

    def test_su_cache(self):
        cloudkey = CloudKey('root', 'qwsxdcfv', BASE_URL)
        res = cloudkey.user.whoami()
        self.assertEqual(res['username'], 'root')
        cloudkey.act_as_user('sebest')
        res = cloudkey.user.whoami()
        self.assertEqual(res['username'], 'sebest')

if __name__ == '__main__':
    unittest.main()
