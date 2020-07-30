import time
import unittest

from src.beans import NetAddress, NodeInformation
from src.factory import create_node_manger_by_node_info
from synchronized_set import SynchronizedSet


class StandardNetworkCase(unittest.TestCase):

    def test_start_and_teardown(self):
        alice_information = NodeInformation(NetAddress(port=2999), birthtime=50, name='alice')
        alice = create_node_manger_by_node_info(alice_information)
        alice.start()
        time.sleep(2)
        self.assertEqual(alice.master, alice_information)
        alice.dispatch()
        alice.kill()

    def test_simple_handshake(self):
        global alice, bob, peter
        try:
            alice_information = NodeInformation(NetAddress(port=3002), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4002), birthtime=100, name='bob')
            self.start_and_check_master_and_connection(alice_information, bob_information)
        finally:
            alice.kill()
            bob.kill()

    def test_shutdown_if_other_is_lost(self):
        global alice, bob, peter
        try:
            alice_information = NodeInformation(NetAddress(port=3005), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4061), birthtime=100, name='bob')
            self.start_and_check_master_and_connection(alice_information, bob_information)
            bob.kill()
            time.sleep(8)
            self.assertEqual(alice.running, False)
            self.assertEqual(bob.running, False)
        finally:
            alice.kill()
            bob.kill()

    def test_reentry_if_name_is_same(self):
        global alice, alice2, bob, peter
        try:
            alice_information = NodeInformation(NetAddress(port=3001), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4001), birthtime=100, name='bob')
            self.start_and_check_master_and_connection(alice_information, bob_information)
            alice.dispatch()
            time.sleep(3)
            self.assertEqual(SynchronizedSet({alice_information}), bob.dispatched)
            alice2_information = NodeInformation(NetAddress(port=3015), birthtime=50, name='alice')
            alice2 = create_node_manger_by_node_info(alice2_information)
            time.sleep(10)
            alice2.start()
            time.sleep(3)
            self.assertEqual(SynchronizedSet({}), bob.dispatched)
            self.assertEqual(SynchronizedSet({alice2_information}), bob.connected)

        finally:
            alice.kill()
            alice2.kill()
            bob.kill()

    def start_and_check_master_and_connection(self, alice_information, bob_information):
        global alice, bob
        alice = create_node_manger_by_node_info(alice_information)
        bob = create_node_manger_by_node_info(bob_information)
        alice.start()
        time.sleep(3)
        bob.start()
        time.sleep(3)
        self.assertEqual(alice.connected, SynchronizedSet({bob_information}))
        self.assertEqual(bob.connected, SynchronizedSet({alice_information}))
        time.sleep(8)
        self.assertEqual(alice.master, alice_information)
        self.assertEqual(bob.master, alice_information)


def set_up_peter_bob_alice(alice_information, bob_information, peter_information, by_port=False):
    alice = create_node_manger_by_node_info(alice_information, vote_by_port=by_port)
    bob = create_node_manger_by_node_info(bob_information, vote_by_port=by_port)
    peter = create_node_manger_by_node_info(peter_information, vote_by_port=by_port)
    alice.start()
    bob.start()
    peter.start()
    time.sleep(5)
    return alice, bob, peter
