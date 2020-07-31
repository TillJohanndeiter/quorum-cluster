"""
Tests for data class message dict.
"""

import unittest
import threading
import time
from synchronized_set import SynchronizedSet

from src.beans import NodeInformation, NetAddress
from src.message_dict import MessageDict, DEFAULT_MESSAGE, DISPATCH_MESSAGE, MESSAGE_SEPARATOR, JSON_SEPARATOR

alice_information = NodeInformation(NetAddress(port=4040), name='alice')
bob_information = NodeInformation(NetAddress(port=5050), name='bob')
peter_information = NodeInformation(NetAddress(port=6060), name='peter')

bob_information.wish_master = peter_information

class MessageDictTestCase(unittest.TestCase):
    """
    Tests for data class message dict.
    """

    def test_adding(self):
        """
        Adds two text messages to instance of message dict and checks if get_next_message
        retrieves correctly contacted string with message separator.
        :return:
        """
        message_dict = MessageDict(bob_information)
        message_dict.add_message_for_node("test", alice_information)
        message_dict.add_message_for_node("test2", alice_information)
        nextMsg = message_dict.get_next_message(alice_information)
        self.assertEqual('test--__--test2', nextMsg)

    def test_add_multiple_nodes(self):
        """
        First add three nodes to dict, then add two text messages for all added
        nodes and checks for each if if get_next_message
        retrieves correctly contacted string with message separator.
        :return: None
        """
        message_dict = MessageDict(bob_information)
        message_dict.add_node(alice_information)
        message_dict.add_node(bob_information)
        message_dict.add_node(peter_information)
        message_dict.add_message_for_all_nodes("test")
        message_dict.add_message_for_all_nodes("test2")
        self.assertEqual('test--__--test2', message_dict.get_next_message(alice_information))
        self.assertEqual('test--__--test2', message_dict.get_next_message(bob_information))
        self.assertEqual('test--__--test2', message_dict.get_next_message(peter_information))

    def test_clear(self):
        """
        Test if clear methods remove all queues form message dict
        :return: None
        """
        message_dict = MessageDict(bob_information)
        message_dict.add_message_for_node("test", alice_information)
        message_dict.clear()
        self.assertEqual(len(message_dict.dict), 0)

    def test_default_message(self):
        """
        Test if in case of a empty message queue correct default message is returned.
        :return: None
        """
        message_dict = MessageDict(bob_information)
        message_dict.add_message_for_node("test", alice_information)
        nextMsg = message_dict.get_next_message(alice_information)
        self.assertEqual('test', nextMsg)
        self.assertEqual(DEFAULT_MESSAGE + JSON_SEPARATOR + peter_information.to_json(), message_dict.get_next_message(alice_information))

    def test_wait_unit_all_received(self):
        """
        Checks if wait_until_everybody_received to not stuck in an
        endless loop after all messages has been taken.
        :return: None
        """
        message_dict = MessageDict(bob_information)
        message_dict.add_node(bob_information)
        message_dict.add_node(peter_information)
        message_dict.add_dispatch_message(alice_information, SynchronizedSet(set()))
        t = threading.Thread(target=self.take_message, args=(message_dict,))
        t.start()
        message_dict.wait_until_everybody_received(DISPATCH_MESSAGE + MESSAGE_SEPARATOR + alice_information.to_json())

    def take_message(self, message_dict):
        """"
        Help method that take the messages to simulate PingMan who send
        messages.
        """
        time.sleep(1)
        message_dict.get_next_message(bob_information)
        message_dict.get_next_message(peter_information)


if __name__ == '__main__':
    unittest.main()
