USERNAME='admin'
PASSWORD='admin'
BASE_URL='http://api.dmcloud.net'
FARM='test_farm'

import unittest
import os, time

from cloudkey import Farm, NotFound

class FarmerTest(unittest.TestCase):
    def setUp(self):
        self.farm = Farm(USERNAME, PASSWORD, BASE_URL)

    def tearDown(self):
        self.farm.remove(name=FARM)

    def test_get_node_notfound(self):
        self.assertRaises(NotFound, self.farm.get_node, name=FARM, node='node-1')

    def test_get_node(self):
        res = self.farm.add_node(name=FARM, node='node-1')
        self.assertEqual(res, None)
        res = self.farm.get_node(name=FARM, node='node-1')
        self.assertEqual(res, {'comment': '', 'enabled': False, 'name': 'node-1', 'weight': 1})

    def test_add_node(self):
        res = self.farm.add_node(name=FARM, node='node-1')
        self.assertEqual(res, None)
        res = self.farm.get_node(name=FARM, node='node-1')
        self.assertEqual(res, {'comment': '', 'enabled': False, 'name': 'node-1', 'weight': 1})

    def test_add_node_with_weight(self):
        res = self.farm.add_node(name=FARM, node='node-2', weight=10)
        self.assertEqual(res, None)
        res = self.farm.get_node(name=FARM, node='node-2')
        self.assertEqual(res, {'comment': '', 'enabled': False, 'name': 'node-2', 'weight': 10})

    def test_add_node_with_weight_disabled(self):
        res = self.farm.add_node(name=FARM, node='node-3', weight=10, enabled=False)
        self.assertEqual(res, None)
        res = self.farm.get_node(name=FARM, node='node-3')
        self.assertEqual(res, {'comment': '', 'enabled': False, 'name': 'node-3', 'weight': 10})

    def test_add_node_with_update(self):
        res = self.farm.add_node(name=FARM, node='node-4', weight=10, enabled=False)
        self.assertEqual(res, None)
        res = self.farm.get_node(name=FARM, node='node-4')
        self.assertEqual(res, {'comment': '', 'enabled': False, 'name': 'node-4', 'weight': 10})
        res = self.farm.add_node(name=FARM, node='node-4', weight=10, enabled=True)
        self.assertEqual(res, None)
        res = self.farm.get_node(name=FARM, node='node-4')
        self.assertEqual(res, {'comment': '', 'enabled': True, 'name': 'node-4', 'weight': 10})

    def test_add_node_with_comment_enabled(self):
        res = self.farm.add_node(name=FARM, node='node-5', weight=10, enabled=True, comment='super node')
        self.assertEqual(res, None)
        res = self.farm.get_node(name=FARM, node='node-5')
        self.assertEqual(res, {'comment': 'super node', 'enabled': True, 'name': 'node-5', 'weight': 10})

    def test_list_node(self):
        for i in range(10):
            res = self.farm.add_node(name=FARM, node='node-%s' % i)
            self.assertEqual(res, None)
        res = self.farm.list_node(name=FARM)
        self.assertEqual(len(res), 10)
        for node in res:
            self.assertEqual(set(node.keys()), set(['comment', 'enabled', 'name', 'weight']))
            self.assertEqual(node['enabled'], False)
            self.assertEqual(node['weight'], 1)
            self.assertEqual(node['comment'], '')
            self.assertEqual(node['name'][:5], 'node-')

if __name__ == '__main__':
    unittest.main()
