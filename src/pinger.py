import struct
import time
from threading import Thread
from socket import AF_INET, SOCK_STREAM, IPPROTO_TCP, SOMAXCONN, SHUT_RDWR, socket, timeout
from synchronized_set import SynchronizedSet
from observer import Observable
from src.message_dict import MessageDict
from src.observers import UpdateValue
from src.beans import NodeInformation


NEW_EXISTING_NODE = 'HANDSHAKE_WITH_EXISTING_BEFORE'
INCOMING_MESSAGE = 'INCOMING_MESSAGE'
CONNECTION_LOST = 'CONNECTION_LOST'

TIME_TO_SEND_DISPATCH_MESSAGE = 10
MAX_PING_TRY = 10
SECOND_INTERVAL_PING_TRY = 0.1
UTF_8 = 'utf8'


class PingMan(Observable):

    def __init__(self, own_information: NodeInformation, message_dict: MessageDict,
                 connected: SynchronizedSet):
        super().__init__()
        self.own_information = own_information
        self.message_dict = message_dict
        self.connected = connected
        self.server_socket_thread = Thread(target=self.__set_up_server_socket)
        self.ping_thread = Thread(target=self.__send_ping_to_all)
        self.running = False
        self.server_socket = None

    def start(self):
        self.running = True
        self.server_socket_thread.start()
        self.ping_thread.start()

    def kill(self):
        self.running = False
        if self.server_socket is not None:
            try:
                self.server_socket.shutdown(SHUT_RDWR)
            except OSError:
                pass
            self.server_socket.close()

        if self.server_socket_thread.is_alive():
            self.server_socket_thread.join()

    def __set_up_server_socket(self):

        in_socket = None
        try:
            self.server_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
            self.server_socket.bind(self.own_information.net_address.to_tuple())
            self.server_socket.listen(SOMAXCONN)
            # print('{} start server socket at {}'.format(self.own_information.name,
            #                                         self.own_information.net_address.to_json()))

            while self.running:
                try:
                    in_socket, _ = self.server_socket.accept()
                    raw_msglen = self.read_number_of_bytes(in_socket, 4)
                    if raw_msglen:
                        msg_len = struct.unpack('>I', raw_msglen)[0]
                        msg = self.read_number_of_bytes(in_socket, msg_len)
                        if msg is not None:
                            msg = msg.decode(UTF_8)
                            print('{} received msg: \n {} \n'.format(self.own_information.name, msg))
                            self.notify(UpdateValue(INCOMING_MESSAGE, msg))
                    if in_socket is not None:
                        in_socket.close()
                except timeout:
                    pass
                except OSError:
                    pass
        finally:
            self.server_socket.close()

    def read_number_of_bytes(self, sock, num_bytes_to_read):
        data = bytearray()
        while len(data) < num_bytes_to_read:
            packet = sock.recv(num_bytes_to_read - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def update_message(self, in_socket: socket):

        raw_msglen = self.read_number_of_bytes(in_socket, 4)
        if raw_msglen:
            msg_len = struct.unpack('>I', raw_msglen)[0]
            msg = self.read_number_of_bytes(in_socket, msg_len)
            if msg is not None:
                msg = msg.decode(UTF_8)
                print('{} received msg: \n {} \n'.format(self.own_information.name, msg))
                self.notify(UpdateValue(INCOMING_MESSAGE, msg))
        in_socket.close()

    def __send_ping_to_target(self, target: NodeInformation):
        target_address = target.net_address
        ping_counter = 0
        suc_connected = False
        message = self.message_dict.get_next_message(target)
        message_with_header = struct.pack('>I', len(message)) + message.encode(UTF_8)
        client_socket = None
        while not suc_connected \
                and self.running \
                and target in self.connected \
                and ping_counter < MAX_PING_TRY:

            try:
                client_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
                client_socket.connect(target_address.to_tuple())
                client_socket.sendall(message_with_header)
                suc_connected = True
            except:
                ping_counter += 1
                time.sleep(SECOND_INTERVAL_PING_TRY)
            finally:
                if client_socket is not None:
                    client_socket.close()

        if ping_counter == MAX_PING_TRY and target in self.connected:
            print('{} could not send \n {}  \n to send to {}'.format(self.own_information.name, message, target.name))
            self.notify(UpdateValue(CONNECTION_LOST, target))
        else:
            print('{} send \n {}  \n to send to {}'.format(self.own_information.name, message, target.name))

    def __send_ping_to_all(self):

        while self.running:
            copy = self.connected.copy()
            ping_threads = []
            for target in copy:
                target_ping_thread = Thread(target=self.__send_ping_to_target, args=(target,))
                ping_threads.append(target_ping_thread)
                target_ping_thread.start()

            for target_ping_thread in ping_threads:
                target_ping_thread.join()
