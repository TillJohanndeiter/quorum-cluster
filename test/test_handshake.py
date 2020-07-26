import unittest

from src.connection_manger import NodeManger
from src.message_dict import MessageDict
from src.pinger import PingMan
from src.handshake import Handshaker
from src.beans import *
from synchronized_set import  SynchronizedSet

alice_information = NodeInformation(NetAddress(port=4042), status='OK', name='alice')
bob_information = NodeInformation(NetAddress(port=5052), status='OK', name='bob')
peter_information = NodeInformation(NetAddress(port=6062), status='OK', name='peter')
all_information = {alice_information, bob_information, peter_information}
DUMMY_DICT = MessageDict()


class HandshakeTestCase(unittest.TestCase):

    def test_only_handshake_from_new_side(self):
        alice_handshake = Handshaker(alice_information)
        alice_pingman = PingMan(alice_information, DUMMY_DICT)
        bob_handshake = Handshaker(bob_information)
        bob_pingman = PingMan(bob_information, DUMMY_DICT)
        peter_handshake = Handshaker(peter_information)
        aliceManger = NodeManger(alice_information, alice_pingman, DUMMY_DICT)
        alice_handshake.attach(aliceManger)
        bobManger = NodeManger(bob_information, bob_pingman, DUMMY_DICT)
        bob_handshake.attach(bobManger)
        peter_pingman = PingMan(peter_information, DUMMY_DICT)
        peterManger = NodeManger(peter_information, peter_pingman, DUMMY_DICT)
        peter_handshake.attach(peterManger)
        alice_handshake.start()
        time.sleep(1)
        bob_handshake.start()
        time.sleep(1)
        peter_handshake.start()
        time.sleep(5)
        self.assertEqual(SynchronizedSet({bob_information, peter_information}), aliceManger.connected)
        self.assertEqual(SynchronizedSet({peter_information}), bobManger.connected)
        self.assertEqual(SynchronizedSet({}), peterManger.connected)
        print('finished test')
        alice_handshake.end()
        bob_handshake.end()
        peter_handshake.end()

    def test_complete_handshake(self):
        alice_handshake = Handshaker(alice_information)
        alice_dict = MessageDict()
        alice_pingman = PingMan(alice_information, alice_dict)
        bob_handshake = Handshaker(bob_information)
        bob_dict = MessageDict()
        bob_pingman = PingMan(bob_information, bob_dict)
        peter_handshake = Handshaker(peter_information)
        peter_dict = MessageDict()
        peter_pingman = PingMan(peter_information, peter_dict)

        aliceManger = NodeManger(alice_information, alice_pingman, alice_dict)
        alice_handshake.attach(aliceManger)
        alice_pingman.attach(aliceManger)

        bobManger = NodeManger(bob_information, bob_pingman, bob_dict)
        bob_pingman.attach(bobManger)
        bob_handshake.attach(bobManger)

        peter_manger = NodeManger(peter_information, peter_pingman, peter_dict)
        peter_handshake.attach(peter_manger)
        peter_pingman.attach(peter_manger)

        alice_pingman.start()
        alice_handshake.start()
        time.sleep(3)

        bob_pingman.start()
        bob_handshake.start()
        time.sleep(3)

        peter_pingman.start()
        peter_handshake.start()
        time.sleep(10)

        self.assertEqual(SynchronizedSet({bob_information, peter_information}), aliceManger.connected)
        self.assertEqual(SynchronizedSet({alice_information, peter_information}), bobManger.connected)
        self.assertEqual(SynchronizedSet({alice_information, bob_information}), peter_manger.connected)
        print('finished test')
        alice_handshake.end()
        alice_pingman.kill()
        bob_handshake.end()
        bob_pingman.kill()
        peter_handshake.end()
        peter_pingman.kill()

if __name__ == '__main__':
    unittest.main()
