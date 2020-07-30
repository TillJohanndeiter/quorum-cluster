import unittest
import threading
import time
from synchronized_set import SynchronizedSet

from src.beans import NodeInformation, NetAddress
from src.message_dict import MessageDict, DEFAULT_MESSAGE, DISPATCH_MESSAGE, MESSAGE_SEPARATOR, JSON_SEPARATOR

alice_information = NodeInformation(NetAddress(port=4040), name='alice')
bob_information = NodeInformation(NetAddress(port=5050), name='bob')
peter_information = NodeInformation(NetAddress(port=6060), name='peter')


class MessageDictTestCase(unittest.TestCase):

    def test_adding(self):
        message_dict = MessageDict()
        message_dict.add_message_for_node("test", alice_information)
        message_dict.add_message_for_node("test2", alice_information)
        nextMsg = message_dict.get_next_message(alice_information)
        self.assertEqual('test--__--test2', nextMsg)

    def test_add_multiple_nodes(self):
        message_dict = MessageDict()
        message_dict.add_node(alice_information)
        message_dict.add_node(bob_information)
        message_dict.add_node(peter_information)
        message_dict.add_message_for_all_nodes("test")
        message_dict.add_message_for_all_nodes("test2")
        self.assertEqual('test--__--test2', message_dict.get_next_message(alice_information))
        self.assertEqual('test--__--test2', message_dict.get_next_message(bob_information))
        self.assertEqual('test--__--test2', message_dict.get_next_message(peter_information))

    def test_clear(self):
        message_dict = MessageDict()
        message_dict.add_message_for_node("test", alice_information)
        message_dict.clear()
        self.assertEqual(len(message_dict.dict), 0)

    def test_default_message(self):
        message_dict = MessageDict()
        message_dict.add_message_for_node("test", alice_information)
        nextMsg = message_dict.get_next_message(alice_information)
        self.assertEqual('test', nextMsg)
        self.assertEqual(DEFAULT_MESSAGE + JSON_SEPARATOR, message_dict.get_next_message(alice_information))

    def test_wait_unit_all_received(self):
        message_dict = MessageDict()
        message_dict.add_node(bob_information)
        message_dict.add_node(peter_information)
        message_dict.add_dispatch_message(alice_information, SynchronizedSet(set()))
        t = threading.Thread(target=self.take_message, args=(message_dict,))
        t.start()
        message_dict.wait_untill_everybody_received(DISPATCH_MESSAGE + MESSAGE_SEPARATOR + alice_information.to_json())



    def take_message(self, message_dict):
        time.sleep(1)
        message_dict.get_next_message(bob_information)
        message_dict.get_next_message(peter_information)


if __name__ == '__main__':
    unittest.main()
