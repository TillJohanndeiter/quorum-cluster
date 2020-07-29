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
            alice_information = NodeInformation(NetAddress(port=3001), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4001), birthtime=100, name='bob')
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

    def start_and_check_master_and_connection(self, alice_information, bob_information):
        global alice, bob
        alice = create_node_manger_by_node_info(alice_information)
        bob = create_node_manger_by_node_info(bob_information)
        alice.start()
        time.sleep(3)
        bob.start()
        time.sleep(2)
        self.assertEqual(alice.connected, SynchronizedSet({bob_information}))
        self.assertEqual(bob.connected, SynchronizedSet({alice_information}))
        time.sleep(8)
        self.assertEqual(alice.master, alice_information)
        self.assertEqual(bob.master, alice_information)


def set_up_peter_bob_alice(alice_information, bob_information, peter_information):
    alice = create_node_manger_by_node_info(alice_information)
    bob = create_node_manger_by_node_info(bob_information)
    peter = create_node_manger_by_node_info(peter_information)
    alice.start()
    bob.start()
    peter.start()
    time.sleep(5)
    return alice, bob, peter


class AdvancedNetworkCase(unittest.TestCase):

    def test_handshake_with_three_nodes(self):
        global alice, bob, peter
        try:
            alice_information = NodeInformation(NetAddress(port=3000), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4000), birthtime=100, name='bob')
            peter_information = NodeInformation(NetAddress(port=5000), birthtime=200, name='peter')
            alice = create_node_manger_by_node_info(alice_information)
            bob = create_node_manger_by_node_info(bob_information)
            peter = create_node_manger_by_node_info(peter_information)
            alice.start()
            bob.start()
            time.sleep(5)
            self.assertEqual(alice.connected, SynchronizedSet({bob_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information}))
            self.assertEqual(alice.master, alice_information)
            self.assertEqual(bob.master, alice_information)
            peter.start()
            time.sleep(8)
            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information, peter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information}))
            self.assertEqual(alice.master, alice_information)
            self.assertEqual(bob.master, alice_information)
            self.assertEqual(peter.master, alice_information)
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
            alice, bob, peter = set_up_peter_bob_alice(alice_information, bob_information, peter_information)
            time.sleep(2)
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

    def test_dispatching(self):
        global alice, bob, peter
        alice_information = NodeInformation(NetAddress(port=6013), name='alice')
        bob_information = NodeInformation(NetAddress(port=7015), name='bob')
        peter_information = NodeInformation(NetAddress(port=8016), name='peter')
        try:
            alice, bob, peter = set_up_peter_bob_alice(alice_information, bob_information, peter_information)
            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information, peter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information}))
            peter.dispatch()
            time.sleep(8)
            self.assertEqual(alice.connected, SynchronizedSet({bob_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information}))
            self.assertEqual(alice.lost, SynchronizedSet({}))
            self.assertEqual(bob.lost, SynchronizedSet({}))
            self.assertEqual(alice.dispatched, SynchronizedSet({peter_information}))
            self.assertEqual(bob.dispatched, SynchronizedSet({peter_information}))
        finally:
            alice.kill()
            bob.kill()
            peter.kill()

    def test_changing_master(self):
        global alice, bob, peter, dieter
        try:
            alice_information = NodeInformation(NetAddress(port=3010), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4100), birthtime=100, name='bob')
            peter_information = NodeInformation(NetAddress(port=5150), birthtime=200, name='peter')
            dieter_information = NodeInformation(NetAddress(port=8005), birthtime=60, name='dieter')
            alice, bob, peter = set_up_peter_bob_alice(alice_information, bob_information, peter_information)
            dieter = create_node_manger_by_node_info(dieter_information)
            dieter.start()
            time.sleep(3)
            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information, dieter_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information, peter_information, dieter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information, dieter_information}))
            self.assertEqual(dieter.connected, SynchronizedSet({alice_information, bob_information, peter_information}))

            alice.kill()
            time.sleep(8)

            self.assertEqual(bob.connected, SynchronizedSet({peter_information, dieter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({bob_information, dieter_information}))
            self.assertEqual(dieter.connected, SynchronizedSet({bob_information, peter_information}))

            self.assertEqual(bob.lost, SynchronizedSet({alice_information}))
            self.assertEqual(peter.lost, SynchronizedSet({alice_information}))
            self.assertEqual(dieter.lost, SynchronizedSet({alice_information}))

            self.assertEqual(bob.dispatched, SynchronizedSet({}))
            self.assertEqual(peter.dispatched, SynchronizedSet({}))
            self.assertEqual(dieter.dispatched, SynchronizedSet({}))

            self.assertEqual(bob.master, dieter_information)
            self.assertEqual(peter.master, dieter_information)
            self.assertEqual(dieter.master, dieter_information)

        finally:
            alice.kill()
            bob.kill()
            peter.kill()
            dieter.kill()
