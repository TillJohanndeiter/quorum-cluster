import unittest
import time
from src.pinger import PingMan
from src.beans import NetAddress, NodeInformation
from src.message_dict import MessageDict

DUMMY_DICT = MessageDict()


class SocketCommunicatorTestCase(unittest.TestCase):

    def test_server_socket_set_up(self):
        pass

    def test_connection(self):
        alice_information = NodeInformation(NetAddress(port=4040), status='OK', name='alice')
        bob_information = NodeInformation(NetAddress(port=5050), status='OK', name='bob')
        alice = PingMan(alice_information, DUMMY_DICT, connected=[bob_information])
        self.assertEqual(alice.connected, [bob_information])
        self.assertEqual(alice.sucDisconnected, [])
        self.assertEqual(alice.failed, [])
        bob = PingMan(bob_information, DUMMY_DICT)
        bob.start()
        alice.start()
        time.sleep(5)
        self.assertEqual(alice.connected, [bob_information])
        bob.kill()
        alice.kill()

    def test_reentries(self):
        pass

    def test_unexpected_shutdown(self):
        aliceAddress = NetAddress(port=5050, )
        bobsAddress = NetAddress(port=4040, )
        alice = PingMan(aliceAddress, connected=[bobsAddress])
        self.assertEqual(alice.connected, [bobsAddress])
        alice.start()
        time.sleep(5)
        self.assertEqual(alice.failed, [bobsAddress])
        alice.kill()


if __name__ == '__main__':
    unittest.main()
