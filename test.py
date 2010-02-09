import unittest
import os

from dkapi import *
import simplejson as json

class DkapiTestBase(unittest.TestCase):

    def setUp(self):
        self.client = DkAPI('sebest', 'sebest', 'dk_api.sebest.dev.dailymotion.com')
        self.client.media_reset()

    def tearDown(self):
        pass

    def test_media_create(self):
        media_id = self.client.media_create()

        self.assertEqual(type(media_id), dict)
        self.assertEqual(media_id.keys(), ['id'])
        self.assertEqual(len(media_id['id']), 24)

    def test_media_info(self):
        media_id = self.client.media_create()
        res = self.client.media_info(id=media_id['id'])

        self.assertEqual(type(res), dict)
        self.assertEqual(res.keys(), ['id'])
        self.assertEqual(len(res['id']), 24)

        self.assertRaises(InvalidArgument,  self.client.media_info, id=media_id['id'][:-2])

    def test_media_delete(self):
        media_id = self.client.media_create()
        res = self.client.media_delete(id=media_id['id'])

        self.assertEqual(type(res), str)
        self.assertEqual(res, 'Media deleted')

        self.assertRaises(NotFound, self.client.media_info, id=media_id['id'])

        self.assertRaises(NotFound, self.client.media_delete, id=media_id['id'])

    def test_media_meta_set(self):
        media_id = self.client.media_create()
        res = self.client.media_meta_set(id=media_id['id'], key='mykey', value='value')

        self.assertEqual(type(res), str)
        self.assertEqual(res, 'Meta set')

        self.assertRaises(MissingArgument, self.client.media_meta_set, id=media_id['id'], key='mykey')
        self.assertRaises(MissingArgument, self.client.media_meta_set, id=media_id['id'], value='myvalue')
        self.assertRaises(MissingArgument, self.client.media_meta_set, id=media_id['id'])

    def test_media_meta_get(self):
        media_id = self.client.media_create()
        self.client.media_meta_set(id=media_id['id'], key='mykey', value='value')

        res = self.client.media_meta_get(id=media_id['id'], key='mykey')
        self.assertEqual(type(res), str)
        self.assertEqual(res, 'value')

        self.assertRaises(NotFound, self.client.media_meta_get, id=media_id['id'], key='invalid_key')
        self.assertRaises(NotFound, self.client.media_meta_get, id=media_id['id'], key=[])

    def test_media_meta_remove(self):
        media_id = self.client.media_create()
        self.client.media_meta_set(id=media_id['id'], key='mykey', value='value')

        res = self.client.media_meta_remove(id=media_id['id'], key='mykey')
        self.assertEqual(type(res), str)
        self.assertEqual(res, 'Meta removed')
        
        res = self.client.media_meta_remove(id=media_id['id'], key='mykey')
        self.assertEqual(type(res), str)
        self.assertEqual(res, 'Meta removed')

        self.assertRaises(NotFound, self.client.media_meta_get, id=media_id['id'], key='mykey')

    def test_media_list(self):
        res = self.client.media_list()
        self.assertEqual(res, [])

        medias = []
        for i in range(25):
            medias.append(self.client.media_create())
        res = self.client.media_list()
        self.assertEqual(res, medias)

        res = self.client.media_list(page=1)
        self.assertEqual(res, medias[:10])

        res = self.client.media_list(page=2)
        self.assertEqual(res, medias[10:20])

        res = self.client.media_list(page=2, count=6)
        self.assertEqual(res, medias[6:12])

#        fields = json.dumps(['assets.source.status', 'metas'])
#        filter = json.dumps({'assets.source.status' : 'ready'})
#        for i in self.client.media_list(filter=filter, fields=fields):
#            print i['id']

#        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()
