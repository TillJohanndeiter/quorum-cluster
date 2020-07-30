"""
Provides Handshake class which send message per broadcast and will listen to incoming messages
"""

import time
import threading

from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_UDP, SO_BROADCAST, \
    SOL_SOCKET, SO_REUSEPORT, SHUT_RDWR, error
from observer import Observable

from src.beans import NetAddress, NodeInformation, node_information_from_json, UpdateValue

DEFAULT_BROADCAST = NetAddress(host="<broadcast>", port=5555)
MESSAGE_LENGTH = 500
TIMEOUT_BROADCAST = 0.2
ENCODE_UTF_8 = 'utf8'
NEW_ENTERING_NODE = 'HANDSHAKE_WITH_ENTERING_NODE'


class Handshake(Observable):
    """
    Class responsible for send message per broadcast and listen to incoming messages.
    Notify observers about incoming.
    """

    def __init__(self,
                 own_information: NodeInformation,
                 broadcast_address: NetAddress = DEFAULT_BROADCAST):
        super(Handshake, self).__init__()
        self.own_information = own_information
        self.broadcast_address = broadcast_address
        self.broadcast_thread = threading.Thread(target=self.__send_broadcast)
        self.collect_thread = threading.Thread(target=self.__collect_entering_node)
        self.running = False
        self.introduce_socket = None
        self.response_socket = None

    def start(self):
        """
        Start listing for incoming messages and send thread.
        """
        self.running = True
        self.collect_thread.start()
        time.sleep(1)
        self.broadcast_thread.start()

    def kill(self):
        """
        Close all sockets and will join listing and send threads
        :return: None
        """
        self.running = False
        if self.broadcast_thread.is_alive():
            self.broadcast_thread.join()
        if self.response_socket is not None:
            try:
                self.response_socket.shutdown(SHUT_RDWR)
            except (error, OSError, ValueError):
                pass
            self.response_socket.close()
        if self.collect_thread.is_alive():
            self.collect_thread.join()

    def __send_broadcast(self):
        """
        Start broadcast and send own node information other nodes in network
        :return: None
        """
        self.introduce_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.introduce_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.introduce_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.introduce_socket.settimeout(TIMEOUT_BROADCAST)
        message = self.own_information.to_json()
        self.introduce_socket.sendto(bytes(message, encoding=ENCODE_UTF_8),
                                     (self.broadcast_address.host, self.broadcast_address.port))
        self.introduce_socket.close()

    def __collect_entering_node(self):
        """
        Listen on Broadcast address for entering nodes and will notify
        node manger if new send information
        :return: None
        """
        self.response_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.response_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.response_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.response_socket.bind(('', self.broadcast_address.port))
        while self.running:
            data, _ = self.response_socket.recvfrom(MESSAGE_LENGTH)
            if data != b'':
                threading.Thread(target=self.__add_node_info_and_send_own, args=(data,)).start()
        self.response_socket.close()

    def __add_node_info_and_send_own(self, data):
        """
        Help Method to notify observer in own Thread
        :param data: data from socket who send information
        :return: None
        """
        data = data.decode(encoding=ENCODE_UTF_8)
        node_information = node_information_from_json(data)
        self.notify(UpdateValue(NEW_ENTERING_NODE, node_information))
