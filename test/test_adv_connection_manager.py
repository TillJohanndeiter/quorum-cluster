"""
Contain class that cover network use cases especially changes of master use cases.
"""
import time
import unittest

from src.beans import NetAddress, NodeInformation
from src.factory import create_node_manger_by_node_info
from synchronized_set import SynchronizedSet

from test.test_simple_connection_manger import set_up_peter_bob_alice


class AdvancedNetworkCase(unittest.TestCase):

    def test_handshake_with_three_nodes(self):
        """
        Set up two nodes. Check if both are connected and have same master. Then
        will start third instance and will again check if connected and same master
        :return: None
        """
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
        """
        Test if a reentering of an instance bob and bob2 on different port is
        registered by instances in a network of three nodes.
        :return: None
        """
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
        """
        Test if unexpected shutdown/kill is registered by other instances
        and marked as lost and removed from connected.
        :return: None
        """
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
        """
        Check if in a network of three nodes dispatching from node peter
        is registered by others nodes. So node is in dispatched and not in connected
        or lost
        :return: None
        """
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
        """
        Check if in a network of four nodes master is correctly determined and after
        master is killed other nodes can determined a new master by using TimeStrategy
        :return: None
        """
        global alice, bob, peter, dieter
        try:
            alice_information = NodeInformation(NetAddress(port=3012), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4101), birthtime=100, name='bob')
            peter_information = NodeInformation(NetAddress(port=5151), birthtime=200, name='peter')
            dieter_information = NodeInformation(NetAddress(port=3013), birthtime=60, name='dieter')
            alice, bob, peter = set_up_peter_bob_alice(alice_information, bob_information, peter_information)
            dieter = create_node_manger_by_node_info(dieter_information, vote_by_port=True, debug=True)
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

    def test_changing_master_by_port(self):
        """
            Check if in a network of four nodes master is correctly determined and after
            master is killed other nodes can determined a new master by using PortStrategy
            :return: None
        """
        global alice, bob, peter, dieter
        try:
            alice_information = NodeInformation(NetAddress(port=3051), birthtime=50, name='alice')
            bob_information = NodeInformation(NetAddress(port=4111), birthtime=100, name='bob')
            peter_information = NodeInformation(NetAddress(port=5155), birthtime=200, name='peter')
            dieter_information = NodeInformation(NetAddress(port=3121), birthtime=60, name='dieter')
            alice, bob, peter = set_up_peter_bob_alice(alice_information, bob_information, peter_information, True)
            dieter = create_node_manger_by_node_info(dieter_information, vote_by_port=True, debug=True)
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
        """
        Check if nodes make shutdown, if 2 of 4 nodes are killed-
        :return: None
        """
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
        """
        Check if network still determine master correctly if a slave/non-master has
        been killed.
        :return: None
        """
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
        """
        Test correct determination of master in a network of four nodes after
        master determined first dispatched.
        :return: None
        """
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
