BASE_URL=None
USERNAME=None
PASSWORD=None

SKIP_SU=True
ROOT_USERNAME=None
ROOT_PASSWORD=None
SWITCH_USER=None

SKIP_FARMER=True
FARMER_USERNAME=None
FARMER_PASSWORD=None
FARMER_FARM=None

try:
    from local_config import *
except ImportError:
    pass

if not USERNAME: USERNAME = raw_input('Username: ')
if not PASSWORD: PASSWORD = raw_input('Password: ')

if not SKIP_SU and not ROOT_USERNAME: ROOT_USERNAME = raw_input('Root Username (optional): ')
if ROOT_USERNAME:
    if not ROOT_PASSWORD: ROOT_PASSWORD = raw_input('Root Password: ')
    if not SWITCH_USER: SWITCH_USER = raw_input('SU Username (optional): ')
else:
    if not SKIP_SU: print "SU tests will be skipped"
if not SKIP_FARMER and not FARMER_USERNAME: FARMER_USERNAME = raw_input('Farmer Username (optional): ')
if FARMER_USERNAME:
    if not FARMER_PASSWORD: FARMER_PASSWORD = raw_input('Farmer Password: ')
    if not FARMER_FARM: FARMER_FARM = raw_input('Farmer Farm: ')
else:
    if not SKIP_FARMER: print "Farmer tests will be skipped"

import os, time
import unittest
from cloudkey import CloudKey, NotFound, InvalidArgument, MissingArgument, AuthorizationRequired, AuthenticationFailed

class CloudKeyMediaDeleteTest(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
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

class CloudKeyMediaInfoTest(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_info(self):
        media = self.cloudkey.media.create()
        res = self.cloudkey.media.info(id=media['id'])

        self.assertEqual(type(res), dict)
        self.assertEqual(set(res.keys()), set([u'meta', u'id', u'assets']))
        self.assertEqual(len(res['id']), 24)

    def test_media_not_found(self):
        self.assertRaises(NotFound, self.cloudkey.media.info, id='1b87186c84e1b015a0000000')

    def test_invalid_media_id(self):
        self.assertRaises(InvalidArgument, self.cloudkey.media.info, id='b87186c84e1b015a0000000')

class CloudKeyMediaCreateTest(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_create(self):
        media = self.cloudkey.media.create()

        self.assertEqual(type(media), dict)
        self.assertEqual(media.keys(), ['id'])
        self.assertEqual(len(media['id']), 24)

class CloudKeyMediaMetaTest(unittest.TestCase):
    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
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

class CloudKeyMediaAssetUrl(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
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

class CloudKeyMediaAssetTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_media_set_asset_source(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media['id'], preset='source', url=media_url)
        self.assertNotEqual(res, None)
        self.assertEqual(res['status'], 'queued')

    def test_media_set_asset_existing_video(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        preset='flv_h263_mp3'
        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media['id'], preset=preset, url=media_url)
        self.assertNotEqual(res, None)
        self.assertEqual(res['status'], 'queued')
        res = self.wait_for_asset(media['id'], preset)

        res = self.cloudkey.media.get_asset(id=media['id'], preset=preset)
        self.assertEqual('status' in res.keys(), True)
        self.assertEqual(res['status'], 'ready')

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
        self.assertNotEqual(res, None)
        self.assertEqual(res['status'], 'queued')
        res = self.wait_for_remove_asset(media['id'], 'source', 20)
        self.assertEqual(res, True)

        self.cloudkey.media.set_asset(id=media['id'], preset='source', url=media_url)
        print self.cloudkey.media.list_asset(id=media['id'])
        res = self.cloudkey.media.remove_asset(id=media['id'], preset='source')
        self.assertNotEqual(res, None)
        self.assertEqual(res['status'], 'queued')

        res = self.wait_for_remove_asset(media['id'], 'source')
        self.assertEqual(res, True)
        self.assertRaises(NotFound, self.cloudkey.media.get_asset, id=media['id'], preset='source')

    def test_media_process_asset(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        media = self.cloudkey.media.create()
        res = self.cloudkey.media.set_asset(id=media['id'], preset='source', url=media_url)
        res = self.cloudkey.media.process_asset(id=media['id'], preset='flv_h263_mp3')
        self.assertNotEqual(res, None)
        self.assertEqual(res['status'], 'queued')
        res = self.cloudkey.media.process_asset(id=media['id'], preset='mp4_h264_aac')
        self.assertNotEqual(res, None)
        self.assertEqual(res['status'], 'queued')
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
        self.assertEqual(set(res.keys()), set(['name', 'status', 'duration', 'filesize']))
        res = self.cloudkey.media.get_asset(id= media['id'], preset='mp4_h264_aac')
        self.assertEqual(res['status'], 'ready')
        self.assertEqual(set(res.keys()), set(['name', 'status', 'duration', 'filesize']))

#        my_broken_video.avi

    def test_media_process_asset_no_source(self):
        media = self.cloudkey.media.create()
        res = self.cloudkey.media.process_asset(id=media['id'], preset='flv_h263_mp3')
        self.assertNotEqual(res, None)
        self.assertEqual(res['status'], 'error')
        self.assertRaises(NotFound, self.cloudkey.media.get_asset, id= media['id'], preset='flv_h263_mp3')

class CloudKeyMediaPublishTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_publish(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/video.3gp')
        media_url = media_info['url']

        presets = ['flv_h263_mp3', 'mp4_h264_aac', 'mp4_h264_aac_hq', 'jpeg_thumbnail_small', 'jpeg_thumbnail_medium', 'jpeg_thumbnail_large']

        media = self.cloudkey.media.publish(url=media_url, presets=presets)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media['id'], preset=preset)
            self.assertEqual(res['status'], 'pending')

        for preset in presets:
            res = self.wait_for_asset(media['id'], preset)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media['id'], preset=preset)
            self.assertEqual(res['status'], 'ready')
            self.assertEqual(set(res.keys()), set(['name', 'status', 'duration', 'filesize']))

    def test_publish_source_error(self):
        media_info = self.cloudkey.file.upload_file('.fixtures/broken_video.avi')
        media_url = media_info['url']

        presets = ['flv_h263_mp3', 'mp4_h264_aac', 'mp4_h264_aac_hq']

        media = self.cloudkey.media.publish(url=media_url, presets=presets)

        for preset in presets:
            res = self.wait_for_asset(media['id'], preset)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media['id'], preset=preset)
            self.assertEqual(res['status'], 'error')
            self.assertEqual(res.keys(), ['status', 'name'])

    def test_publish_url_error(self):
        media_url = 'http://localhost/'

        presets = ['flv_h263_mp3', 'mp4_h264_aac', 'mp4_h264_aac_hq']

        media = self.cloudkey.media.publish(url=media_url, presets=presets)

        for preset in presets:
            res = self.wait_for_asset(media['id'], preset, 10)
            self.assertEqual(res, False)

        for preset in presets:
            res = self.cloudkey.media.get_asset(id= media['id'], preset=preset)
            self.assertEqual(res['status'], 'error')
            self.assertEqual(res.keys(), ['status', 'name'])

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


class CloudKeyFileTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
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
        self.assertEqual(media_info['size'], 92543)
        self.assertEqual(media_info['name'], 'video')
        self.assertEqual('url' in media_info.keys(), True)

class CloudKeyMediaListTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_empty_list(self):
        res = self.cloudkey.media.list()
        self.assertEqual(res, [])

    def test_list(self):
        medias = []
        for i in range(25):
            medias.append({u'meta': {}, u'id': self.cloudkey.media.create()['id'], u'assets': {}})
        res = self.cloudkey.media.list()
        self.assertEqual(res, medias)

    def test_pagination(self):
        medias = []
        for i in range(25):
            medias.append({u'meta': {}, u'id': self.cloudkey.media.create()['id'], u'assets': {}})

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
            self.assertEqual(len(i.keys()), 3)
            self.assertEqual(i['meta'].get('mykey-2'), 'value-2')
            self.assertEqual(i['meta'].get('mykey-3'), 'value-3')
            self.assertEqual(i['meta'].get('mykey-1'), None)

        filter = {'meta.mykey-1' : '42'}
        res = self.cloudkey.media.list(filter=filter)
        self.assertEqual(len(res), 12)
        for i in res:
            self.assertEqual(len(i.keys()), 3)
            self.assertEqual(set(i.keys()), set([u'meta', u'id', u'assets']))


class CloudKeyMediaTest(unittest.TestCase):

    def setUp(self):
        self.cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
        self.cloudkey.media.reset()

    def tearDown(self):
        self.cloudkey.media.reset()

    def test_media_create(self):
        media = self.cloudkey.media.create()

        self.assertEqual(type(media), dict)
        self.assertEqual(media.keys(), ['id'])
        self.assertEqual(len(media['id']), 24)


if ROOT_USERNAME and ROOT_PASSWORD and SWITCH_USER:
    class CloudKeyAuthTest(unittest.TestCase):
        def test_anonymous(self):
            cloudkey = CloudKey(None, None)
            self.assertRaises(AuthorizationRequired, cloudkey.user.whoami)

        def test_normal_user(self):
            cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
            res = cloudkey.user.whoami()
            self.assertEqual(res['username'], USERNAME)

        def test_normal_user_su(self):
            cloudkey = CloudKey(USERNAME, PASSWORD, base_url=BASE_URL)
            cloudkey.act_as_user(SWITCH_USER)
            res = cloudkey.user.whoami()
            self.assertEqual(res['username'], USERNAME)

        def test_super_user(self):
            cloudkey = CloudKey(ROOT_USERNAME, ROOT_PASSWORD)
            res = cloudkey.user.whoami()
            self.assertEqual(res['username'], ROOT_USERNAME)

        def test_super_user_su(self):
            cloudkey = CloudKey(ROOT_USERNAME, ROOT_PASSWORD)
            cloudkey.act_as_user(SWITCH_USER)
            res = cloudkey.user.whoami()
            self.assertEqual(res['username'], SWITCH_USER)

        def test_super_user_su_wrong_user(self):
            cloudkey = CloudKey(ROOT_USERNAME, ROOT_PASSWORD)
            cloudkey.act_as_user('unexisting_user')
            self.assertRaises(AuthenticationFailed, cloudkey.user.whoami)

        def test_su_cache(self):
            cloudkey = CloudKey(ROOT_USERNAME, ROOT_PASSWORD)
            res = cloudkey.user.whoami()
            self.assertEqual(res['username'], ROOT_USERNAME)
            cloudkey.act_as_user(SWITCH_USER)
            res = cloudkey.user.whoami()
            self.assertEqual(res['username'], SWITCH_USER)

if FARMER_USERNAME and FARMER_PASSWORD and FARMER_FARM:
    class CloudKeyFarmTest(unittest.TestCase):
        def setUp(self):
            self.cloudkey = CloudKey(FARMER_USERNAME, FARMER_PASSWORD)

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
                self.assertEqual(node['enabled'], False)
                self.assertEqual(node['weight'], 1)
                self.assertEqual(node['comment'], '')
                self.assertEqual(node['name'][:5], 'node-')

if __name__ == '__main__':
    unittest.main()
