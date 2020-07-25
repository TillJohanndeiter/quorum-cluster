import unittest

from src.beans import NodeInformation, NetAddress
from src.message_dict import MessageDict, DEFAULT_MESSAGE

alice_information = NodeInformation(NetAddress(port=4040), status='OK', name='alice')
bob_information = NodeInformation(NetAddress(port=5050), status='OK', name='bob')
peter_information = NodeInformation(NetAddress(port=6060), status='OK', name='peter')
all_information = [alice_information, bob_information, peter_information]


class MessageDictTestCase(unittest.TestCase):

    def test_adding(self):
        message_dict = MessageDict()
        message_dict.add_message_for_node("test", alice_information)
        message_dict.add_message_for_node("test2", alice_information)
        nextMsg = message_dict.get_next_message(alice_information)
        self.assertEqual('test', nextMsg)
        nextMsg = message_dict.get_next_message(alice_information)
        self.assertEqual('test2', nextMsg)

    def test_add_multiple_nodes(self):
        message_dict = MessageDict()
        message_dict.add_message_for_nodes("test", all_information)
        message_dict.add_message_for_nodes("test2", all_information)
        self.assertEqual('test', message_dict.get_next_message(alice_information))
        self.assertEqual('test2', message_dict.get_next_message(alice_information))
        self.assertEqual('test', message_dict.get_next_message(bob_information))
        self.assertEqual('test2', message_dict.get_next_message(bob_information))
        self.assertEqual('test', message_dict.get_next_message(peter_information))
        self.assertEqual('test2', message_dict.get_next_message(peter_information))

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
        self.assertEqual(DEFAULT_MESSAGE, message_dict.get_next_message(alice_information))


if __name__ == '__main__':
    unittest.main()
