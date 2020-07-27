import time
import unittest

from src import beans
from src.beans import NodeInformation, NetAddress
import src.beans


class BeanCase(unittest.TestCase):
    def test_something(self):
        node = NodeInformation(NetAddress(host='1.1.1.1', port=7542), time.time(), name='Till')
        json_string = NodeInformation.to_json(node)
        deserialized_node = src.beans.node_information_from_json(json_string)
        self.assertEqual(node.name, deserialized_node.name)
        self.assertEqual(node.birthtime, deserialized_node.birthtime)
        self.assertEqual(node.net_address, deserialized_node.net_address)
        self.assertEqual(node.net_address.host, deserialized_node.net_address.host)
        self.assertEqual(node.net_address.port, deserialized_node.net_address.port)


if __name__ == '__main__':
    unittest.main()
