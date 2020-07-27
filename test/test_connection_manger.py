import time
import unittest

from src.beans import NetAddress, NodeInformation
from src.factory import create_node_manger_by_node_info
from synchronized_set import SynchronizedSet


class StandardNetworkCase(unittest.TestCase):

    def test_handshake(self):
        global alice, bob, peter
        try:
            alice_information = NodeInformation(NetAddress(port=5000), name='alice')
            bob_information = NodeInformation(NetAddress(port=4000), name='bob')
            peter_information = NodeInformation(NetAddress(port=3000), name='peter')
            alice, bob, peter = self.set_up_peter_bob_alice(alice_information, bob_information, peter_information)
            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information, peter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information}))
        finally:
            alice.kill()
            bob.kill()
            peter.kill()

    def test_kill_detected(self):
        global alice, bob, peter
        try:
            alice_information = NodeInformation(NetAddress(port=6001), name='alice')
            bob_information = NodeInformation(NetAddress(port=7002), name='bob')
            peter_information = NodeInformation(NetAddress(port=8003), name='peter')
            alice, bob, peter = self.set_up_peter_bob_alice(alice_information, bob_information, peter_information)
            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information, peter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information}))

            peter.kill()
            time.sleep(8)
            self.assertEqual(alice.connected, SynchronizedSet({bob_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information}))
            self.assertEqual(alice.lost, SynchronizedSet({peter_information}))
            self.assertEqual(bob.lost, SynchronizedSet({peter_information}))
            self.assertEqual(alice.dispatched, SynchronizedSet({}))
            self.assertEqual(bob.dispatched, SynchronizedSet({}))
        finally:
            alice.kill()
            bob.kill()
            peter.kill()

    def set_up_peter_bob_alice(self, alice_information, bob_information, peter_information):
        alice = create_node_manger_by_node_info(alice_information)
        bob = create_node_manger_by_node_info(bob_information)
        peter = create_node_manger_by_node_info(peter_information)
        alice.start()
        time.sleep(3)
        bob.start()
        time.sleep(3)
        peter.start()
        time.sleep(8)
        return alice, bob, peter

    def test_dispatching(self):
        global alice, bob, peter
        alice_information = NodeInformation(NetAddress(port=6013), name='alice')
        bob_information = NodeInformation(NetAddress(port=7015), name='bob')
        peter_information = NodeInformation(NetAddress(port=8016), name='peter')
        try:
            alice, bob, peter = self.set_up_peter_bob_alice(alice_information, bob_information, peter_information)
            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information, peter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information}))

            peter.dispatch()
            time.sleep(8)
            self.assertEqual(alice.connected, SynchronizedSet({bob_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information}))

            self.assertEqual(alice.dispatched, SynchronizedSet({peter_information}))
            self.assertEqual(bob.dispatched, SynchronizedSet({peter_information}))
            self.assertEqual(alice.lost, SynchronizedSet({}))
            self.assertEqual(bob.lost, SynchronizedSet({}))
        finally:
            alice.kill()
            bob.kill()
            peter.kill()
