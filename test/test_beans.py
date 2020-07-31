"""
Simple test for serialization and deserialization of data class.
"""
import time
import unittest

from src import beans
from src.beans import NodeInformation, NetAddress


class BeanCase(unittest.TestCase):

    def test_serialization_deserialization(self):
        """
        Checks if a instance of NodeInformation can be serialized and json string can be deserialized.
        Checks if each value stays same
        :return: None
        """



        node = NodeInformation(NetAddress(host='1.1.1.1', port=7542), time.time(), name='Till')
        node.wish_master = node
        json_string = NodeInformation.to_json(node)
        deserialized_node = beans.node_information_from_json(json_string)
        self.assertEqual(node.name, deserialized_node.name)
        self.assertEqual(node.birthtime, deserialized_node.birthtime)
        self.assertEqual(node.net_address, deserialized_node.net_address)
        self.assertEqual(node.net_address.host, deserialized_node.net_address.host)
        self.assertEqual(node.net_address.port, deserialized_node.net_address.port)
        self.assertEqual(node.wish_master, deserialized_node)


if __name__ == '__main__':
    unittest.main()
