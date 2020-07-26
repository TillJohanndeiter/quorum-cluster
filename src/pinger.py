from socket import *
import time
from synchronized_set import SynchronizedSet
from threading import Thread
from src.message_dict import MessageDict, DEFAULT_MESSAGE
from src.observers import UpdateValue
from src.beans import NetAddress, NodeInformation, node_information_from_json
from observer import Observable

TIME_TO_SEND_DISPATCH_MESSAGE = 10
LENGTH_OF_RECEIVED_MESSAGE = 1000
MAX_PING_TRY = 5
SECOND_INTERVAL_PING_TRY = 0.1
DISPATCH_MESSAGE = 'BYE'
ENCODE_UTF_8 = 'utf8'
NEW_EXISTING_NODE = 'HANDSHAKE_WITH_EXISTING_BEFORE'


# TODO: Handshake per broadcast!
# TODO: Threadsafety


class PingMan(Observable):

    def __init__(self, ownAddress: NodeInformation, message_dict: MessageDict, connected=None, failed=None,
                 sucDisconnected=None):
        super().__init__()
        if sucDisconnected is None:
            sucDisconnected = SynchronizedSet(set())
        if failed is None:
            failed = SynchronizedSet(set())
        if connected is None:
            connected = SynchronizedSet(set())
        self.message_dict = message_dict
        self.connected = connected
        self.failed = failed
        self.sucDisconnected = sucDisconnected
        self.ownInformation = ownAddress
        self.server_socket = None
        self.client_socket = None
        self.server_socket_thread = Thread(target=self.__start_server_socket)
        self.ping_thread = Thread(target=self.__send_ping_to_all)
        self.running = False

    def start(self):
        self.running = True
        self.server_socket_thread.start()
        self.ping_thread.start()

    def kill(self):
        self.running = False
        try:
            self.server_socket.shutdown(SHUT_RDWR)
        except (error, OSError, ValueError):
            pass
        try:
            self.client_socket.shutdown(SHUT_RDWR)
        except (error, OSError, ValueError):
            pass
        self.client_socket.close()
        self.server_socket.close()
        self.server_socket_thread.join()
        self.ping_thread.join()

    def dispatch_from_network(self):
        time.sleep(TIME_TO_SEND_DISPATCH_MESSAGE)

    def __set_up_server_socket(self):
        global inSocket
        print(
            '{} start server socket at {}'.format(self.ownInformation.name, self.ownInformation.net_address.to_json()))

        try:
            self.server_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
            self.server_socket.bind(self.ownInformation.net_address.to_tuple())
            self.server_socket.listen(SOMAXCONN)
            while self.running:
                try:
                    t = Thread(target=self.bla())
                    t.start()
                except OSError:
                    pass
                finally:
                    inSocket.close()
        except Exception as e:
            print(e)
            print('{} end server socket at {}'.format(self.ownInformation.name,
                                                      self.ownInformation.net_address.to_json()))
        finally:
            self.server_socket.close()

    def bla(self):
        global inSocket
        inSocket, addr = self.server_socket.accept()
        received_bytes = inSocket.recv(LENGTH_OF_RECEIVED_MESSAGE)
        msg = received_bytes.decode(ENCODE_UTF_8)
        if not msg.startswith(DEFAULT_MESSAGE) and msg != '':
            print('{} received message: {}'.format(self.ownInformation.name, msg))
            node_info = node_information_from_json(msg)
            self.notify(UpdateValue(NEW_EXISTING_NODE, node_info))

    def __send_ping_to_target(self, target: NodeInformation):
        target_address = target.net_address
        ping_counter = 0
        sucConnected = False
        # print("{} try to send to {} with address {}".format(self.ownInformation.name, target.name, target.net_address.to_tuple()))
        message = self.message_dict.get_next_message(target)
        while self.running and ping_counter < MAX_PING_TRY and not sucConnected:
            try:
                self.client_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
                self.client_socket.connect(target_address.to_tuple())
                print("{} send message : \n {} \n to {}".format(self.ownInformation.name, message, target.name))
                self.client_socket.send(bytes(message, ENCODE_UTF_8))
                sucConnected = True
            except:
                ping_counter += 1
                time.sleep(SECOND_INTERVAL_PING_TRY)
            finally:
                self.client_socket.close()

        if ping_counter == MAX_PING_TRY:
            print('connection error between {} and {}'.format(self.ownInformation.name, target.name))
            if target in self.connected:
                self.connected.remove(target)
            self.failed.add(target)

    def __send_ping_to_all(self):

        ping_thread = []

        while self.running:
            for target in self.connected:
                t = Thread(target=self.__send_ping_to_target, args=(target,))
                ping_thread.append(t)
                t.start()

            for t in ping_thread:
                t.join()

            time.sleep(3)

    def __start_server_socket(self):
        return self.__set_up_server_socket()
