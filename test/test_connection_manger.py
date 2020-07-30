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

    def test_reenter_with_same_name(self):
        global alice, bob, peter
        try:
            alice_information = NodeInformation(NetAddress(port=3199), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4199), birthtime=100, name='bob')
            peter_information = NodeInformation(NetAddress(port=5199), birthtime=200, name='peter')
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

            bob.dispatch()
            time.sleep(8)

            self.assertEqual(alice.dispatched, SynchronizedSet({bob_information}))
            self.assertEqual(peter.dispatched, SynchronizedSet({bob_information}))

            bob_information = NodeInformation(NetAddress(port=4500), birthtime=100, name='bob')
            renter_bob = create_node_manger_by_node_info(bob_information)
            renter_bob.start()
            time.sleep(8)

            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information}))
            self.assertEqual(renter_bob.connected, SynchronizedSet({alice_information, peter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information}))

            self.assertEqual(alice.dispatched, SynchronizedSet({}))
            self.assertEqual(renter_bob.dispatched, SynchronizedSet({}))
            self.assertEqual(peter.dispatched, SynchronizedSet({}))


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

    def test_changing_master_by_birthtime(self):
        global alice, bob, peter, dieter
        try:
            alice_information = NodeInformation(NetAddress(port=3012), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4101), birthtime=100, name='bob')
            peter_information = NodeInformation(NetAddress(port=5151), birthtime=200, name='peter')
            dieter_information = NodeInformation(NetAddress(port=3013), birthtime=60, name='dieter')
            alice, bob, peter = set_up_peter_bob_alice(alice_information, bob_information, peter_information)
            dieter = create_node_manger_by_node_info(dieter_information, vote_by_port=True)
            dieter.start()
            time.sleep(3)
            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information, dieter_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information, peter_information, dieter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information, dieter_information}))
            self.assertEqual(dieter.connected, SynchronizedSet({alice_information, bob_information, peter_information}))
            self.assertEqual(alice.master, alice_information)
            self.assertEqual(bob.master, alice_information)
            self.assertEqual(peter.master, alice_information)
            self.assertEqual(dieter.master, alice_information)
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


#TODO: sometimes test fail
    def test_changing_master_by_port(self):
        global alice, bob, peter, dieter
        try:
            alice_information = NodeInformation(NetAddress(port=3051), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4111), birthtime=100, name='bob')
            peter_information = NodeInformation(NetAddress(port=5155), birthtime=200, name='peter')
            dieter_information = NodeInformation(NetAddress(port=3121), birthtime=60, name='dieter')
            alice, bob, peter = set_up_peter_bob_alice(alice_information, bob_information, peter_information, True)
            dieter = create_node_manger_by_node_info(dieter_information, vote_by_port=True)
            dieter.start()
            time.sleep(3)
            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information, dieter_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information, peter_information, dieter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information, dieter_information}))
            self.assertEqual(dieter.connected, SynchronizedSet({alice_information, bob_information, peter_information}))
            self.assertEqual(alice.master, alice_information)
            self.assertEqual(bob.master, alice_information)
            self.assertEqual(peter.master, alice_information)
            self.assertEqual(dieter.master, alice_information)
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

    def test_shutdown_if_two_of_four_be_killed(self):
        global alice, bob, peter, dieter
        try:
            alice_information = NodeInformation(NetAddress(port=3055), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4115), birthtime=100, name='bob')
            peter_information = NodeInformation(NetAddress(port=5155), birthtime=200, name='peter')
            dieter_information = NodeInformation(NetAddress(port=3125), birthtime=60, name='dieter')
            alice, bob, peter = set_up_peter_bob_alice(alice_information, bob_information, peter_information)
            dieter = create_node_manger_by_node_info(dieter_information)
            dieter.start()
            time.sleep(3)
            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information, dieter_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information, peter_information, dieter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information, dieter_information}))
            self.assertEqual(dieter.connected, SynchronizedSet({alice_information, bob_information, peter_information}))
            alice.kill()
            bob.kill()
            time.sleep(10)

            self.assertEqual(False, alice.running)
            self.assertEqual(False, bob.running)
            self.assertEqual(False, peter.running)
            self.assertEqual(False, dieter.running)

        finally:
            alice.kill()
            bob.kill()
            peter.kill()
            dieter.kill()

    def test_slave_is_killed_master_stay_same(self):
        global alice, bob, peter, dieter
        try:
            alice_information = NodeInformation(NetAddress(port=3009), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4180), birthtime=100, name='bob')
            peter_information = NodeInformation(NetAddress(port=5130), birthtime=200, name='peter')
            dieter_information = NodeInformation(NetAddress(port=3661), birthtime=60, name='dieter')
            alice, bob, peter = set_up_peter_bob_alice(alice_information, bob_information, peter_information)
            dieter = create_node_manger_by_node_info(dieter_information, vote_by_port=True)
            dieter.start()
            time.sleep(3)
            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information, dieter_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information, peter_information, dieter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information, dieter_information}))
            self.assertEqual(dieter.connected, SynchronizedSet({alice_information, bob_information, peter_information}))
            self.assertEqual(alice.master, alice_information)
            self.assertEqual(bob.master, alice_information)
            self.assertEqual(peter.master, alice_information)
            self.assertEqual(dieter.master, alice_information)
            bob.kill()
            time.sleep(8)

            self.assertEqual(alice.connected, SynchronizedSet({peter_information, dieter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, dieter_information}))
            self.assertEqual(dieter.connected, SynchronizedSet({alice_information, peter_information}))

            self.assertEqual(alice.lost, SynchronizedSet({bob_information}))
            self.assertEqual(peter.lost, SynchronizedSet({bob_information}))
            self.assertEqual(dieter.lost, SynchronizedSet({bob_information}))

            self.assertEqual(bob.dispatched, SynchronizedSet({}))
            self.assertEqual(peter.dispatched, SynchronizedSet({}))
            self.assertEqual(dieter.dispatched, SynchronizedSet({}))

            self.assertEqual(alice.master, alice_information)
            self.assertEqual(peter.master, alice_information)
            self.assertEqual(dieter.master, alice_information)

        finally:
            alice.kill()
            bob.kill()
            peter.kill()
            dieter.kill()

    def test_changing_master_after_dispatching(self):
        global alice, bob, peter, dieter
        try:
            alice_information = NodeInformation(NetAddress(port=3010), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4100), birthtime=100, name='bob')
            peter_information = NodeInformation(NetAddress(port=5150), birthtime=200, name='peter')
            dieter_information = NodeInformation(NetAddress(port=3011), birthtime=60, name='dieter')
            alice, bob, peter = set_up_peter_bob_alice(alice_information, bob_information, peter_information)
            dieter = create_node_manger_by_node_info(dieter_information, vote_by_port=True)
            dieter.start()
            time.sleep(3)
            self.assertEqual(alice.connected, SynchronizedSet({peter_information, bob_information, dieter_information}))
            self.assertEqual(bob.connected, SynchronizedSet({alice_information, peter_information, dieter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({alice_information, bob_information, dieter_information}))
            self.assertEqual(dieter.connected, SynchronizedSet({alice_information, bob_information, peter_information}))
            self.assertEqual(alice.master, alice_information)
            self.assertEqual(bob.master, alice_information)
            self.assertEqual(peter.master, alice_information)
            self.assertEqual(dieter.master, alice_information)
            alice.dispatch()
            time.sleep(8)

            self.assertEqual(bob.connected, SynchronizedSet({peter_information, dieter_information}))
            self.assertEqual(peter.connected, SynchronizedSet({bob_information, dieter_information}))
            self.assertEqual(dieter.connected, SynchronizedSet({bob_information, peter_information}))

            self.assertEqual(bob.dispatched, SynchronizedSet({alice_information}))
            self.assertEqual(peter.dispatched, SynchronizedSet({alice_information}))
            self.assertEqual(dieter.dispatched, SynchronizedSet({alice_information}))

            self.assertEqual(bob.lost, SynchronizedSet({}))
            self.assertEqual(peter.lost, SynchronizedSet({}))
            self.assertEqual(dieter.lost, SynchronizedSet({}))

            self.assertEqual(bob.master, dieter_information)
            self.assertEqual(peter.master, dieter_information)
            self.assertEqual(dieter.master, dieter_information)

        finally:
            alice.kill()
            bob.kill()
            peter.kill()
            dieter.kill()
