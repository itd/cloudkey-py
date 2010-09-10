BASE_URL=None
USER_ID=None
API_KEY=None

SKIP_SU=True
ROOT_USER_ID=None
ROOT_API_KEY=None
SWITCH_USER_ID=None

SKIP_FARMER=True
FARMER_USER_ID=None
FARMER_API_KEY=None
FARMER_FARM=None
FARMER_URL=None

try:
    from local_config import *
except ImportError:
    print 'No local_config.py found!'
    pass

if not USER_ID: USER_ID = raw_input('Username: ')
if not API_KEY: API_KEY = raw_input('Password: ')

if not SKIP_SU and not ROOT_USER_ID: ROOT_USER_ID = raw_input('Root username (optional): ')
if ROOT_USER_ID:
    if not ROOT_API_KEY: ROOT_API_KEY = raw_input('Root password: ')
    if not SWITCH_USER_ID: SWITCH_USER_ID = raw_input('SU username (optional): ')
else:
    if not SKIP_SU: print "SU tests will be skipped"
if not SKIP_FARMER and not FARMER_USER_ID: FARMER_USER_ID = raw_input('Farmer username (optional): ')
if FARMER_USER_ID:
    if not FARMER_API_KEY: FARMER_API_KEY = raw_input('Farmer password: ')
    if not FARMER_FARM: FARMER_FARM = raw_input('Farmer farm: ')
else:
    if not SKIP_FARMER: print "Farmer tests will be skipped"

import os, time
import urlparse
import unittest

from cloudkey import CloudKey
from cloudkey import SecLevel

# TODO: import the usefull methods and class in this file to make it autonomous
from cloudkey import AuthenticationError, NotFound, InvalidParameter, Exists

def wait_for_asset(media_id, asset_name, wait=60):
    cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
    for i in range(wait):
        asset = cloudkey.media.get_asset(id=media_id, preset=asset_name)
        if asset['status'] != 'ready':
            if asset['status'] == 'error':
                return False
            time.sleep(1)
            continue
        return True
    raise Exception('timeout exceeded')


class CloudKeyMediaDeleteTest(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_delete(self):
        media = self.cloudkey.media.create()
        res = self.cloudkey.media.delete(id=media)

        self.assertEqual(res, None)

        self.assertRaises(NotFound, self.cloudkey.media.info, id=media)

    def test_media_not_found(self):
        self.assertRaises(NotFound, self.cloudkey.media.delete, id='1b87186c84e1b015a0000000')

    def test_invalid_media_id(self):
        self.assertRaises(InvalidParameter, self.cloudkey.media.delete, id='b87186c84e1b015a0000000')

class CloudKeyMediaInfoTest(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_info(self):
        media = self.cloudkey.media.create()
        res = self.cloudkey.media.info(id=media)

        self.assertEqual(type(res), dict)
        self.assertEqual(set(res.keys()), set([u'meta', u'id', u'assets', u'created']))
        self.assertEqual(len(res['id']), 24)

    def test_media_not_found(self):
        self.assertRaises(NotFound, self.cloudkey.media.info, id='1b87186c84e1b015a0000000')

    def test_invalid_media_id(self):
        self.assertRaises(InvalidParameter, self.cloudkey.media.info, id='b87186c84e1b015a0000000')

class CloudKeyMediaCreateTest(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_create(self):
        media = self.cloudkey.media.create()

        self.assertEqual(type(media), unicode)
        self.assertEqual(len(media), 24)

class CloudKeyMediaMetaTest(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_set_get(self):
        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_meta(id=media, key='mykey', value='my_value')
        self.assertEqual(res, None)

        res = self.cloudkey.media.get_meta(id=media, key='mykey')
        self.assertEqual(type(res), unicode)
        self.assertEqual(res, 'my_value')

    def test_media_not_found(self):
        self.assertRaises(NotFound, self.cloudkey.media.set_meta, id='1b87186c84e1b015a0000000', key='mykey', value='my_value')

    def test_invalid_media_id(self):
        self.assertRaises(InvalidParameter, self.cloudkey.media.set_meta, id='b87186c84e1b015a0000000', key='mykey', value='my_value')

    def test_missing_argument(self):
        media = self.cloudkey.media.create()

        self.assertRaises(InvalidParameter, self.cloudkey.media.set_meta, id=media, key='mykey')
        self.assertRaises(InvalidParameter, self.cloudkey.media.set_meta, id=media, value='myvalue')
        self.assertRaises(InvalidParameter, self.cloudkey.media.set_meta, id=media)
        self.assertRaises(InvalidParameter, self.cloudkey.media.get_meta, id=media)
        self.assertRaises(InvalidParameter, self.cloudkey.media.remove_meta, id=media)

    def test_set_meta_update(self):
        media = self.cloudkey.media.create()

        res = self.cloudkey.media.set_meta(id=media, key='mykey', value='value')
        self.assertEqual(res, None)

        res = self.cloudkey.media.set_meta(id=media, key='mykey', value='my_new_value')
        self.assertEqual(res, None)

        res = self.cloudkey.media.get_meta(id=media, key='mykey')
        self.assertEqual(type(res), unicode)
        self.assertEqual(res, 'my_new_value')

    def test_set_meta_unicode(self):
        media = self.cloudkey.media.create()

        res = self.cloudkey.media.set_meta(id=media, key=u'u_mykey', value=u'u_value')
        self.assertEqual(res, None)

        res = self.cloudkey.media.get_meta(id=media, key=u'u_mykey')
        self.assertEqual(type(res), unicode)
        self.assertEqual(res, 'u_value')

    def test_meta_not_found(self):
        media = self.cloudkey.media.create()

        self.assertRaises(NotFound, self.cloudkey.media.get_meta, id=media, key='invalid_key')
        self.assertRaises(InvalidParameter, self.cloudkey.media.get_meta, id=media, key=[])
        self.assertRaises(NotFound, self.cloudkey.media.get_meta, id=media, key=100)

    def test_invalid_key(self):
        media = self.cloudkey.media.create()

    def test_list(self):
        media = self.cloudkey.media.create()

        res = self.cloudkey.media.list_meta(id=media)
        self.assertEqual(type(res), dict)
        self.assertEqual(len(res), 0)

        for i in range(10):
            self.cloudkey.media.set_meta(id=media, key='mykey-%d' % i, value='value-%d' % i)

        res = self.cloudkey.media.list_meta(id=media)
        self.assertEqual(type(res), dict)
        self.assertEqual(len(res.keys()), 10)

        for i in range(10):
            self.assertEqual(res['mykey-%d' %i], 'value-%d' % i)

    def test_remove(self):
        media = self.cloudkey.media.create()
        self.cloudkey.media.set_meta(id=media, key='mykey', value='value')

        res = self.cloudkey.media.remove_meta(id=media, key='mykey')
        self.assertEqual(res, None)

        self.assertRaises(NotFound, self.cloudkey.media.remove_meta, id=media, key='mykey')
        self.assertRaises(NotFound, self.cloudkey.media.get_meta, id=media, key='mykey')

class CloudKeyMediaAssetUrl(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']
        media = self.cloudkey.media.create()
        self.media_id = media
        self.cloudkey.media.set_asset(id=self.media_id, preset='source', url=media_url)

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_media_get_asset_url_preview(self):
        preset = 'jpeg_thumbnail_small'

        self.cloudkey.media.process_asset(id=self.media_id, preset=preset)
        wait_for_asset(self.media_id, preset)
        url = self.cloudkey.media.get_asset_url(id=self.media_id, preset=preset)

        parsed = urlparse.urlparse(url)
        spath = parsed.path.split('/')
        self.assertEqual(len(spath), 4)
        preset_name, ext = spath[-1].split('.')
        self.assertTrue('-' in preset_name)
        self.assertTrue(ext, preset.split('_')[0])
        self.assertEqual(preset_name.split('-')[0], preset)

    def test_media_get_asset_url_video(self):
        preset = 'mp4_h264_aac'

        self.cloudkey.media.process_asset(id=self.media_id, preset=preset)
        wait_for_asset(self.media_id, preset)
        url = self.cloudkey.media.get_asset_url(id=self.media_id, preset=preset)

        parsed = urlparse.urlparse(url)
        self.assertTrue('cdn' in parsed.netloc)
        spath = parsed.path.split('/')
        preset_name, ext = spath[-1].split('.')
        self.assertTrue('-' in preset_name)
        self.assertTrue(ext, preset.split('_')[0])
        self.assertEqual(preset_name.split('-')[0], preset)
        self.assertEqual(len(spath), 5)
        self.assertEqual(spath[1], 'route')

class CloudKeyMediaStreamUrl(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()
        media = self.cloudkey.media.create()
        self.media_id = media

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_media_get_stream_url(self):
        url = self.cloudkey.media.get_stream_url(id=self.media_id)
        # TODO test returned URL + sec levels
        url = self.cloudkey.media.get_stream_url(id=self.media_id, seclevel=SecLevel.DELEGATE|SecLevel.IP, expires=time.time()+60*60)

class CloudKeyMediaAssetTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_media_set_asset_source(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media, preset='source', url=media_url)
        self.assertEqual(res, None)

    def test_media_set_asset_source_with_callback(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media, preset='source', url=media_url, callback_url='http://atm-02.int.dmcloud.net:5000/test')
        self.assertEqual(res, None)
        res = self.wait_for_asset(media, 'source')
        self.assertTrue(res)

    def test_media_set_asset_existing_video(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        preset='flv_h263_mp3'
        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media, preset=preset, url=media_url)
        self.assertEqual(res, None)
        res = self.wait_for_asset(media, preset)

        res = self.cloudkey.media.get_asset(id=media, preset=preset)
        self.assertTrue('status' in res.keys())
        self.assertEqual(res['status'], 'ready')

    def wait_for_asset(self, media_id, asset_name, wait=60):
        for i in range(wait):
            asset = self.cloudkey.media.get_asset(id=media_id, preset=asset_name)
            if asset['status'] != 'ready':
                if asset['status'] == 'error':
                    return False
                time.sleep(1)
                continue
            return True
        raise Exception('timeout exceeded')

    def test_media_get_asset(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media, preset='source', url=media_url)

        res = self.cloudkey.media.get_asset(id= media, preset='source')
        self.assertTrue('status' in res.keys())
        self.assertTrue(res['status'] in ('pending', 'processing'))

        res = self.wait_for_asset(media, 'source')
        self.assertTrue(res)
        res = self.cloudkey.media.get_asset(id=media, preset='source')
        self.assertTrue('status' in res.keys())
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
        res = self.cloudkey.media.set_asset(id=media, preset='source', url=media_url)
        res = self.wait_for_asset(media, 'source')
        self.assertEqual(res, True)

        res = self.cloudkey.media.remove_asset(id=media, preset='source')
        self.assertEqual(res, None)
        res = self.wait_for_remove_asset(media, 'source', 20)
        self.assertEqual(res, True)

        self.cloudkey.media.set_asset(id=media, preset='source', url=media_url)
        res = self.cloudkey.media.remove_asset(id=media, preset='source')
        self.assertEqual(res, None)

        res = self.wait_for_remove_asset(media, 'source')
        self.assertEqual(res, True)
        self.assertRaises(NotFound, self.cloudkey.media.get_asset, id=media, preset='source')

    def test_media_process_asset(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media, preset='source', url=media_url)
        res = self.cloudkey.media.process_asset(id=media, preset='flv_h263_mp3')
        self.assertEqual(res, None)
        res = self.cloudkey.media.process_asset(id=media, preset='mp4_h264_aac')
        self.assertEqual(res, None)
        res = self.cloudkey.media.get_asset(id= media, preset='flv_h263_mp3')
        self.assertEqual(res['status'], 'pending')
        res = self.cloudkey.media.get_asset(id= media, preset='mp4_h264_aac')
        self.assertEqual(res['status'], 'pending')
        res = self.wait_for_asset(media, 'flv_h263_mp3')
        self.assertTrue(res)
        res = self.wait_for_asset(media, 'mp4_h264_aac')
        self.assertTrue(res)
        res = self.cloudkey.media.get_asset(id= media, preset='flv_h263_mp3')
        self.assertEqual(res['status'], 'ready')
        self.assertEqual(set(res.keys()), set(['status', 'container', 'created', 'name', 'video_bitrate', 'video_height', 'audio_bitrate', 'audio_codec', 'file_size', 'duration', 'video_codec', 'video_width', 'global_bitrate', 'created']))
        res = self.cloudkey.media.get_asset(id= media, preset='mp4_h264_aac')
        self.assertEqual(res['status'], 'ready')
        self.assertEqual(set(res.keys()), set(['status', 'container', 'created', 'name', 'video_bitrate', 'video_height', 'audio_bitrate', 'audio_codec', 'file_size', 'duration', 'video_codec', 'video_width', 'global_bitrate', 'created']))

    def test_media_process_asset_alternative_source(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media, preset='source', url=media_url)
        res = self.cloudkey.media.process_asset(id=media, preset='mp4_h264_aac')
        self.assertEqual(res, None)
        res = self.wait_for_asset(media, 'mp4_h264_aac')
        self.assertTrue(res)
        res = self.cloudkey.media.process_asset(id=media, preset='flv_h263_mp3', source_preset='mp4_h264_aac')
        self.assertEqual(res, None)
        res = self.wait_for_asset(media, 'flv_h263_mp3')
        self.assertTrue(res)

    def test_media_process_asset_alternative_source_depends(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media, preset='source', url=media_url)
        res = self.cloudkey.media.process_asset(id=media, preset='mp4_h264_aac')
        res = self.cloudkey.media.process_asset(id=media, preset='flv_h263_mp3', source_preset='mp4_h264_aac')
        res = self.wait_for_asset(media, 'flv_h263_mp3')
        self.assertTrue(res)
        res = self.wait_for_asset(media, 'mp4_h264_aac')
        self.assertTrue(res)

    def test_media_process_asset_no_source(self):
        media = self.cloudkey.media.create()
        self.assertRaises(NotFound, self.cloudkey.media.process_asset, id=media, preset='flv_h263_mp3')
        self.assertRaises(NotFound, self.cloudkey.media.get_asset, id= media, preset='flv_h263_mp3')

    def test_media_process_asset_already_exists(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media, preset='source', url=media_url)
        res = self.cloudkey.media.process_asset(id=media, preset='flv_h263_mp3')
        self.assertEqual(res, None)

        self.assertRaises(Exists, self.cloudkey.media.process_asset, id=media, preset='flv_h263_mp3')

class CloudKeyMediaPublishTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_publish(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        presets = ['flv_h263_mp3', 'mp4_h264_aac', 'mp4_h264_aac_hq', 'jpeg_thumbnail_small', 'jpeg_thumbnail_medium', 'jpeg_thumbnail_large']

        media = self.cloudkey.media.publish(url=media_url, presets=presets)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media, preset=preset)
            self.assertEqual(res['status'], 'pending')

        for preset in presets:
            res = self.wait_for_asset(media, preset)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media, preset=preset)
            self.assertEqual(res['status'], 'ready')
            if 'thumbnail' in preset:
                attr = set(['status', 'container', 'name', 'video_height', 'file_size', 'video_codec', 'video_width', 'created'])
            else:
                attr = set(['status', 'container', 'name', 'video_bitrate', 'video_height', 'audio_bitrate', 'audio_codec', 'file_size', 'duration', 'video_codec', 'video_width', 'global_bitrate', 'created'])
            self.assertEqual(set(res.keys()), attr)

    def test_publish_source_error(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/broken.avi')
        media_url = media_info['url']

        presets = ['flv_h263_mp3', 'mp4_h264_aac', 'mp4_h264_aac_hq']

        media = self.cloudkey.media.publish(url=media_url, presets=presets)

        for preset in presets:
            res = self.wait_for_asset(media, preset)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media, preset=preset)
            self.assertEqual(res['status'], 'error')
            self.assertEqual(res.keys(), ['status', 'name'])

    def test_publish_url_error(self):
        media_url = 'http://localhost/'

        presets = ['flv_h263_mp3', 'mp4_h264_aac', 'mp4_h264_aac_hq']

        media = self.cloudkey.media.publish(url=media_url, presets=presets)

        for preset in presets:
            res = self.wait_for_asset(media, preset, 10)
            self.assertFalse(res)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media, preset=preset)
            self.assertEqual(res['status'], 'error')
            self.assertEqual(res.keys(), ['status', 'name'])

    def test_publish_duplicate_preset_error(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/broken.avi')
        media_url = media_info['url']

        presets = ['mp4_h264_aac', 'mp4_h264_aac']
        media = self.cloudkey.media.publish(url=media_url, presets=presets)
        self.assertEqual(type(media), unicode)

    def wait_for_asset(self, media_id, asset_name, wait=60):
        for i in range(wait):
            asset = self.cloudkey.media.get_asset(id=media_id, preset=asset_name)
            if asset['status'] != 'ready':
                if asset['status'] == 'error':
                    return False
                time.sleep(1)
                continue
            return True
        raise Exception('timeout exceeded')


class CloudKeyFileTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_file_upload(self):
        # status url
        res = self.cloudkey.file.upload()
        self.assertTrue('url' in res.keys())

    def test_file_upload_target(self):
        mytarget='http://www.example.com/myform'
        res = self.cloudkey.file.upload(target=mytarget)
        self.assertTrue('url' in res.keys())
        import urlparse
        parsed = urlparse.urlparse(res['url'])
        myqs = urlparse.parse_qs(parsed.query)
        self.assertEqual(myqs.keys() , ['seal', 'uuid', 'target', ])
        self.assertEqual(myqs['target'][0] , mytarget)

    def test_media_upload(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        self.assertEqual(media_info['size'], 92543)
        self.assertEqual(media_info['name'], 'video')
        self.assertTrue('url' in media_info.keys())

    def test_media_upload_nofile(self):
        self.assertRaises(IOError, self.cloudkey.file.upload_file, '.fixtures/nofile.mov')

class CloudKeyMediaListTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_empty_list(self):
        res = self.cloudkey.media.list()
        self.assertEqual(res, [])

    def test_list(self):
        medias = []
        for i in range(30):
            medias.append(self.cloudkey.media.create())
        res = self.cloudkey.media.list()
        self.assertEqual(len(res), 30)

        res_ids = [m for m in res]
        media_ids = [m for m in medias]
        res_ids = sorted(res_ids)
        media_ids = sorted(media_ids)
        self.assertEqual(res_ids, media_ids)
        self.assertEqual(sorted(res), sorted(medias))

    def test_pagination(self):
        medias = []
        for i in range(25):
            medias.append(self.cloudkey.media.create())

        res = self.cloudkey.media.list(page=1, sort=[('created', 1)])
        res = [r for r in res]
        self.assertEqual(res, medias[:10])

        res = self.cloudkey.media.list(page=2, sort=[('created', 1)])
        res = [r for r in res]
        self.assertEqual(res,  medias[10:20])

        res = self.cloudkey.media.list(page=2, count=6, sort=[('created', 1)])
        res = [r for r in res]
        self.assertEqual(res,  medias[6:12])

    def test_invalid_filter(self):
        medias = []
        for i in range(5):
            medias.append(self.cloudkey.media.create())

        self.assertRaises(InvalidParameter, self.cloudkey.media.list,
                          filter = { '$where' : "this.a > 3" })

        self.assertRaises(InvalidParameter, self.cloudkey.media.list,
                          filter = "this.a > 3")

    def test_invalid_fields(self):
        medias = []
        for i in range(5):
            medias.append(self.cloudkey.media.create())

        self.assertRaises(InvalidParameter, self.cloudkey.media.list,
                          fields = "this.a")

    def test_invalid_sort(self):
        medias = []
        for i in range(5):
            medias.append(self.cloudkey.media.create())

        self.assertRaises(InvalidParameter, self.cloudkey.media.list,
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
                    self.cloudkey.media.set_meta(id=media, key='mykey-%d' % i, value='value-%d' % i)
            else:
                self.cloudkey.media.set_meta(id=media, key='mykey-1', value='42')

        fields = ['meta.mykey-2', 'meta.mykey-3']
        filter = {'meta.mykey-1' : 'value-1'}
        res = self.cloudkey.media.list(fields=fields, filter=filter)
        self.assertEqual(len(res), 13)

        for i in res:
            self.assertEqual(len(i.keys()), 3)
            self.assertEqual(i['meta'].get('mykey-2'), 'value-2')
            self.assertEqual(i['meta'].get('mykey-3'), 'value-3')
            self.assertEqual(i['meta'].get('mykey-1'), None)

        filter = {'meta.mykey-1' : '42'}
        res = self.cloudkey.media.list(filter=filter)
        self.assertEqual(len(res), 12)

class CloudKeyMediaTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_media_create(self):
        media = self.cloudkey.media.create()

        self.assertEqual(type(media), unicode)
        self.assertEqual(len(media), 24)


class CloudKeyMediaStatsTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_media_stats(self):
        media = self.cloudkey.media.create()

        #print self.cloudkey.media.stats(id=media)

class CloudKeyUserAssetsTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.cloudkey.encoding_settings.reset()

    def tearDown(self):
        self.cloudkey.encoding_settings.reset()

    def test_enable_asset(self):
        self.cloudkey.encoding_settings.enable_asset(asset='flv_h263_mp3')
        presets = self.cloudkey.encoding_settings.get_active_assets()
        self.assertEqual(presets, ['flv_h263_mp3'])
        self.cloudkey.encoding_settings.enable_asset(asset='flv_h263_mp3')
        presets = self.cloudkey.encoding_settings.get_active_assets()
        self.assertEqual(presets, ['flv_h263_mp3'])
        self.cloudkey.encoding_settings.enable_asset(asset='mp4_h264_aac')
        presets = self.cloudkey.encoding_settings.get_active_assets()
        self.assertEqual(presets, ['flv_h263_mp3', 'mp4_h264_aac'])

    def test_disable_asset(self):
        self.cloudkey.encoding_settings.enable_asset(asset='flv_h263_mp3')
        self.cloudkey.encoding_settings.enable_asset(asset='mp4_h264_aac')
        presets = self.cloudkey.encoding_settings.get_active_assets()
        self.assertEqual(presets, ['flv_h263_mp3', 'mp4_h264_aac'])
        self.cloudkey.encoding_settings.disable_asset(asset='flv_h263_mp3')
        presets = self.cloudkey.encoding_settings.get_active_assets()
        self.assertEqual(presets, ['mp4_h264_aac'])
        self.cloudkey.encoding_settings.disable_asset(asset='flv_h263_mp3')
        presets = self.cloudkey.encoding_settings.get_active_assets()
        self.assertEqual(presets, ['mp4_h264_aac'])
        self.cloudkey.encoding_settings.disable_asset(asset='mp4_h264_aac')
        presets = self.cloudkey.encoding_settings.get_active_assets()
        self.assertEqual(presets, [])

    def test_get_active_assets(self):
        presets = self.cloudkey.encoding_settings.get_active_assets()
        self.assertEqual(presets, [])

        self.cloudkey.encoding_settings.enable_asset(asset='flv_h263_mp3')
        self.cloudkey.encoding_settings.enable_asset(asset='mp4_h264_aac')
        presets = self.cloudkey.encoding_settings.get_active_assets()
        self.assertEqual(presets, ['flv_h263_mp3', 'mp4_h264_aac'])

        self.cloudkey.encoding_settings.disable_asset(asset='flv_h263_mp3')
        self.cloudkey.encoding_settings.disable_asset(asset='mp4_h264_aac')
        presets = self.cloudkey.encoding_settings.get_active_assets()
        self.assertEqual(presets, [])

    def test_get_set_delete_asset_settings(self):
        pass

    def test_get_set_asset_setting(self):
        for preset in ('flv_h263_mp3', 'flv_h263_mp3_ld', 'mp4_h264_aac'):
            self.cloudkey.encoding_settings.set_asset_setting(asset=preset, setting='abitrate', value='128')
            res = self.cloudkey.encoding_settings.get_asset_setting(asset=preset, setting='abitrate')
            self.assertEqual(res, '128')
            self.cloudkey.encoding_settings.set_asset_setting(asset=preset, setting='vbitrate', value='1024')
            res = self.cloudkey.encoding_settings.get_asset_setting(asset=preset, setting='vbitrate')
            self.assertEqual(res, '1024')

class CloudKeyUserTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(ROOT_USER_ID, ROOT_API_KEY, base_url=BASE_URL)
        self.user_ids = []

    def tearDown(self):
        for user_id in self.user_ids:
            self.cloudkey.user.delete(user_id)
            
    def test_perm(self):
        cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
        self.assertRaises(AuthenticationError, cloudkey.user.create, 'titi', 'toto')
        self.assertRaises(AuthenticationError, cloudkey.user.info, 'titi')
        self.assertRaises(AuthenticationError, cloudkey.user.delete, 'titi')
        self.assertRaises(AuthenticationError, cloudkey.user.list)
        self.assertEqual(cloudkey.user.info()['username'], USERNAME)

    def test_create(self):
        user_id = self.cloudkey.user.create('titi', 'toto')
        self.user_ids.append(user_id)

        self.assertEqual(type(user_id), unicode)
        self.assertEqual(len(user_id), 24)

    def test_create_twice(self):
        user_id = self.cloudkey.user.create('titi', 'toto')
        self.user_ids.append(user_id)

        self.assertRaises(Exists, self.cloudkey.user.create, 'titi', 'toto')

    def test_info(self):
        user_id = self.cloudkey.user.create('titi', 'toto')
        self.user_ids.append(user_id)

        i = self.cloudkey.user.info(user_id)
        self.assertEqual(i['username'], 'titi')

    def test_my_info(self):
        i = self.cloudkey.user.info()
        self.assertEqual(i['username'], ROOT_USERNAME)

    def test_list(self):
        users =  self.cloudkey.user.list()
        self.assertEqual(type(users), list)
        for user in users:
            self.assertEqual(type(user), dict)


if ROOT_USER_ID and ROOT_API_KEY and SWITCH_USER_ID:
    class CloudKeyAuthTest(unittest.TestCase):
        def test_anonymous(self):
            cloudkey = CloudKey(None, None, base_url=BASE_URL)
            self.assertRaises(AuthenticationError, cloudkey.user.whoami)

        def test_normal_user(self):
            cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
            res = cloudkey.user.whoami()
            self.assertEqual(res['username'], USERNAME)

        def test_normal_user_su(self):
            cloudkey = CloudKey(USER_ID, API_KEY, base_url=BASE_URL)
            cloudkey.act_as_user(SWITCH_USER_ID)
            self.assertRaises(AuthenticationError, cloudkey.user.whoami)

        def test_super_user(self):
            cloudkey = CloudKey(ROOT_USER_ID, ROOT_API_KEY, base_url=BASE_URL)
            res = cloudkey.user.whoami()
            self.assertEqual(res['username'], ROOT_USERNAME)

        def test_super_user_su(self):
            cloudkey = CloudKey(ROOT_USER_ID, ROOT_API_KEY, base_url=BASE_URL)
            cloudkey.act_as_user(SWITCH_USER_ID)
            res = cloudkey.user.whoami()
            self.assertEqual(res['username'], SWITCH_USERNAME)

        def test_super_user_su_wrong_user(self):
            cloudkey = CloudKey(ROOT_USER_ID, ROOT_API_KEY, base_url=BASE_URL)
            cloudkey.act_as_user('unexisting_user')
            self.assertRaises(AuthenticationError, cloudkey.user.whoami)

        def test_su_cache(self):
            cloudkey = CloudKey(ROOT_USER_ID, ROOT_API_KEY, base_url=BASE_URL)
            res = cloudkey.user.whoami()
            self.assertEqual(res['username'], ROOT_USERNAME)
            cloudkey.act_as_user(SWITCH_USER_ID)
            res = cloudkey.user.whoami()
            self.assertEqual(res['username'], SWITCH_USERNAME)

if False and FARMER_USER_ID and FARMER_API_KEY and FARMER_FARM:
    class CloudKeyFarmTest(unittest.TestCase):
        def setUp(self):
            self.cloudkey = CloudKey(FARMER_USER_ID, FARMER_API_KEY, base_url=FARMER_URL)

        def tearDown(self):
            self.cloudkey.farm.remove(name=FARMER_FARM)

        def test_get_node_notfound(self):
            self.assertRaises(NotFound, self.cloudkey.farm.get_node, name=FARMER_FARM, node='node-1')

        def test_get_node(self):
            res = self.cloudkey.farm.add_node(name=FARMER_FARM, node='node-1')
            self.assertEqual(res, None)
            res = self.cloudkey.farm.get_node(name=FARMER_FARM, node='node-1')
            self.assertEqual(res, {'comment': '', 'enabled': False, 'name': 'node-1', 'weight': 1})

        def test_add_node(self):
            res = self.cloudkey.farm.add_node(name=FARMER_FARM, node='node-1')
            self.assertEqual(res, None)
            res = self.cloudkey.farm.get_node(name=FARMER_FARM, node='node-1')
            self.assertEqual(res, {'comment': '', 'enabled': False, 'name': 'node-1', 'weight': 1})

        def test_add_node_with_weight(self):
            res = self.cloudkey.farm.add_node(name=FARMER_FARM, node='node-2', weight=10)
            self.assertEqual(res, None)
            res = self.cloudkey.farm.get_node(name=FARMER_FARM, node='node-2')
            self.assertEqual(res, {'comment': '', 'enabled': False, 'name': 'node-2', 'weight': 10})

        def test_add_node_with_weight_disabled(self):
            res = self.cloudkey.farm.add_node(name=FARMER_FARM, node='node-3', weight=10, enabled=False)
            self.assertEqual(res, None)
            res = self.cloudkey.farm.get_node(name=FARMER_FARM, node='node-3')
            self.assertEqual(res, {'comment': '', 'enabled': False, 'name': 'node-3', 'weight': 10})

        def test_add_node_with_update(self):
            res = self.cloudkey.farm.add_node(name=FARMER_FARM, node='node-4', weight=10, enabled=False)
            self.assertEqual(res, None)
            res = self.cloudkey.farm.get_node(name=FARMER_FARM, node='node-4')
            self.assertEqual(res, {'comment': '', 'enabled': False, 'name': 'node-4', 'weight': 10})
            res = self.cloudkey.farm.add_node(name=FARMER_FARM, node='node-4', weight=10, enabled=True)
            self.assertEqual(res, None)
            res = self.cloudkey.farm.get_node(name=FARMER_FARM, node='node-4')
            self.assertEqual(res, {'comment': '', 'enabled': True, 'name': 'node-4', 'weight': 10})

        def test_add_node_with_comment_enabled(self):
            res = self.cloudkey.farm.add_node(name=FARMER_FARM, node='node-5', weight=10, enabled=True, comment='super node')
            self.assertEqual(res, None)
            res = self.cloudkey.farm.get_node(name=FARMER_FARM, node='node-5')
            self.assertEqual(res, {'comment': 'super node', 'enabled': True, 'name': 'node-5', 'weight': 10})

        def test_list_node(self):
            for i in range(10):
                res = self.cloudkey.farm.add_node(name=FARMER_FARM, node='node-%s' % i)
                self.assertEqual(res, None)
            res = self.cloudkey.farm.list_node(name=FARMER_FARM)
            self.assertEqual(len(res), 10)
            for node in res:
                self.assertEqual(set(node.keys()), set(['comment', 'enabled', 'name', 'weight']))
                self.assertFalse(node['enabled'])
                self.assertEqual(node['weight'], 1)
                self.assertEqual(node['comment'], '')
                self.assertEqual(node['name'][:5], 'node-')

        def test_select_node(self):
            nodes = ['node-%s.dailymotion.com' % i for i in range(10)]
            for node in nodes:
                res = self.cloudkey.farm.add_node(name=FARMER_FARM, node=node, enabled=True, weight=10)
                self.assertEqual(res, None)
            
            res1 = {}
            for node in nodes:
                res1[node] = self.cloudkey.farm.select_node(name=FARMER_FARM, content=node)
            
            res2 = {}
            for node in nodes:
                res2[node] = self.cloudkey.farm.select_node(name=FARMER_FARM, content=node)

            for node in nodes:
                self.assertEqual(res1[node], res2[node])

if __name__ == '__main__':
    unittest.main()
