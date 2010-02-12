import unittest
import os

from dkapi import *

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

        # update value
        res = self.client.media_meta_set(id=media_id['id'], key='mykey', value='value')
        self.assertEqual(type(res), str)
        self.assertEqual(res, 'Meta set')

        # unicode key/value
        res = self.client.media_meta_set(id=media_id['id'], key=u'u_mykey', value=u'u_value')
        self.assertEqual(type(res), str)
        self.assertEqual(res, 'Meta set')

    def test_media_meta_get(self):
        media_id = self.client.media_create()
        self.client.media_meta_set(id=media_id['id'], key='mykey', value='value')

        res = self.client.media_meta_get(id=media_id['id'], key='mykey')
        self.assertEqual(type(res), str)
        self.assertEqual(res, 'value')

        self.assertRaises(NotFound, self.client.media_meta_get, id=media_id['id'], key='invalid_key')
        self.assertRaises(NotFound, self.client.media_meta_get, id=media_id['id'], key=[])

        # update value
        self.client.media_meta_set(id=media_id['id'], key='mykey', value='new_value')
        res = self.client.media_meta_get(id=media_id['id'], key='mykey')
        self.assertEqual(type(res), str)
        self.assertEqual(res, 'new_value')

        # unicode key/value
        self.client.media_meta_set(id=media_id['id'], key=u'u_mykey', value=u'u_value')
        res = self.client.media_meta_get(id=media_id['id'], key=u'u_mykey')
        self.assertEqual(type(res), str)
        self.assertEqual(res, u'u_value')

    def test_media_meta_remove(self):
        media_id = self.client.media_create()
        self.client.media_meta_set(id=media_id['id'], key='mykey', value='value')

        res = self.client.media_meta_remove(id=media_id['id'], key='mykey')
        self.assertEqual(type(res), str)
        self.assertEqual(res, 'Meta removed')
        
        self.assertRaises(NotFound, self.client.media_meta_remove, id=media_id['id'], key='mykey')

        self.assertRaises(NotFound, self.client.media_meta_get, id=media_id['id'], key='mykey')

    def test_media_meta_list(self):
        media_id = self.client.media_create()
        res = self.client.media_meta_list(id=media_id['id'])
        self.assertEqual(type(res), dict)
        self.assertEqual(len(res.keys()), 0)

        for i in range(10):
            self.client.media_meta_set(id=media_id['id'], key='mykey-%d' % i, value='value-%d' % i)

        res = self.client.media_meta_list(id=media_id['id'])
        self.assertEqual(type(res), dict)
        self.assertEqual(len(res.keys()), 10)

        for i in range(10):
            self.assertEqual(res['mykey-%d' %i], 'value-%d' % i)

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

        x = 0
        for media in medias:
            x += 1
            if x % 2:
                for i in range(5):
                    self.client.media_meta_set(id=media['id'], key='mykey-%d' % i, value='value-%d' % i)
            else:
                self.client.media_meta_set(id=media['id'], key='mykey-1', value='42')

        fields = ['meta.mykey-2', 'meta.mykey-3']
        filter = {'meta.mykey-1' : 'value-1'}
        res = self.client.media_list(fields=fields, filter=filter)
        self.assertEqual(len(res), 13)

        for i in res:
            self.assertEqual(len(i.keys()), 2)
            self.assertEqual(i['meta'].get('mykey-2'), 'value-2')
            self.assertEqual(i['meta'].get('mykey-3'), 'value-3')
            self.assertEqual(i['meta'].get('mykey-1'), None)

        filter = {'meta.mykey-1' : '42'}
        res = self.client.media_list(filter=filter)
        self.assertEqual(len(res), 12)
        for i in res:
            self.assertEqual(len(i.keys()), 1)
            self.assertEqual(i.keys(), ['id'])


if __name__ == '__main__':
    unittest.main()
