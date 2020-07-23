import unittest
import time
from src.SocketCommunicator import SocketCommunicator
from src.flask_server import NetAddressInformation


class SocketCommunicatorTestCase(unittest.TestCase):

    def test_server_socket_set_up(self):
        pass

    def test_connection(self):
        aliceAddress = NetAddressInformation(port=8080)
        bobsAddress = NetAddressInformation(port=7070)
        alice = SocketCommunicator(aliceAddress, connected=[bobsAddress])
        self.assertEqual(alice.connected, [bobsAddress])
        self.assertEqual(alice.sucDisconnected, [])
        self.assertEqual(alice.failed, [])
        bob = SocketCommunicator(bobsAddress, )
        bob.start()
        alice.start()
        time.sleep(5)
        self.assertEqual(alice.connected, [bobsAddress])
        bob.kill()
        alice.kill()

    def test_reentries(self):
        pass

    def test_unexpected_shutdown(self):
        aliceAddress = NetAddressInformation(port=5050, )
        bobsAddress = NetAddressInformation(port=4040, )
        alice = SocketCommunicator(aliceAddress, connected=[bobsAddress])
        self.assertEqual(alice.connected, [bobsAddress])
        alice.start()
        time.sleep(5)
        self.assertEqual(alice.failed, [bobsAddress])
        alice.kill()


if __name__ == '__main__':
    unittest.main()
