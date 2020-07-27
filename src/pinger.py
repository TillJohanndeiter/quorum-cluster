from socket import *
import time
from synchronized_set import SynchronizedSet
from threading import Thread
from src.message_dict import MessageDict
from src.observers import UpdateValue
from src.beans import NodeInformation
from observer import Observable

NEW_EXISTING_NODE = 'HANDSHAKE_WITH_EXISTING_BEFORE'
INCOMING_MESSAGE = 'INCOMING_MESSAGE'
CONNECTION_LOST = 'CONNECTION_LOST'

TIME_TO_SEND_DISPATCH_MESSAGE = 10
LENGTH_OF_RECEIVED_MESSAGE = 1000
MAX_PING_TRY = 5
SECOND_INTERVAL_PING_TRY = 0.1
ENCODE_UTF_8 = 'utf8'


class PingMan(Observable):

    def __init__(self, own_address: NodeInformation, message_dict: MessageDict, connected: SynchronizedSet):
        super().__init__()
        self.ownInformation = own_address
        self.message_dict = message_dict
        self.connected = connected
        self.server_socket_thread = Thread(target=self.__start_server_socket)
        self.ping_thread = Thread(target=self.__send_ping_to_all)
        self.running = False
        self.server_socket = None
        self.client_socket = None

    def start(self):
        self.running = True
        self.server_socket_thread.start()
        self.ping_thread.start()

    def kill(self):
        self.running = False
        try:
            if self.server_socket is not None:
                self.server_socket.shutdown(SHUT_RDWR)
        except (error, OSError, ValueError):
            pass
        try:
            if self.client_socket is not None:
                self.client_socket.shutdown(SHUT_RDWR)
        except (error, OSError, ValueError):
            pass
        if self.client_socket is not None:
            self.client_socket.close()
        if self.server_socket is not None:
            self.server_socket.close()
        self.server_socket_thread.join()
        self.ping_thread.join()

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
                    inSocket, addr = self.server_socket.accept()
                    t = Thread(target=self.__get_client_message, args=(inSocket,))
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

    def __get_client_message(self, in_socket):
        try:
            received_bytes = in_socket.recv(LENGTH_OF_RECEIVED_MESSAGE)
            msg = received_bytes.decode(ENCODE_UTF_8)
            if msg != '':
                self.notify(UpdateValue(INCOMING_MESSAGE, msg))
        except OSError:
            pass

    def __send_ping_to_target(self, target: NodeInformation):
        target_address = target.net_address
        ping_counter = 0
        suc_connected = False
        message = self.message_dict.get_next_message(target)
        while not suc_connected and self.running and target in self.connected and ping_counter < MAX_PING_TRY:
            try:
                self.client_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
                self.client_socket.connect(target_address.to_tuple())
                print("{} send message : \n {} \n to {}".format(self.ownInformation.name, message, target.name))
                self.client_socket.send(bytes(message, ENCODE_UTF_8))
                suc_connected = True
            except Exception as e:
                print(e)
                ping_counter += 1
                time.sleep(SECOND_INTERVAL_PING_TRY)
            finally:
                self.client_socket.close()

        if ping_counter == MAX_PING_TRY and target in self.connected:
            print('connection error between {} and {}'.format(self.ownInformation.name, target.name))
            self.notify(UpdateValue(CONNECTION_LOST, target))

    def __send_ping_to_all(self):

        ping_thread = []

        while self.running:
            copy = self.connected.copy()
            """
            for target in copy:
                t = Thread(target=self.__send_ping_to_target, args=(target,))
                ping_thread.append(t)
                t.start()

            for t in ping_thread:
                t.join()
            """
            for target in copy:
                self.__send_ping_to_target(target)

            time.sleep(SECOND_INTERVAL_PING_TRY * MAX_PING_TRY * len(copy) + 3)

    def __start_server_socket(self):
        return self.__set_up_server_socket()
