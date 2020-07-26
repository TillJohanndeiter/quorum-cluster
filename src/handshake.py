from socket import *
import time
import threading
from observer import Observable
from src.beans import NetAddress, NodeInformation, node_information_from_json
from src.observers import UpdateValue

DEFAULT_BROADCAST = NetAddress(ip_address="<broadcast>", port=5555)
MESSAGE_LENGTH = 1024
TIMEOUT_BROADCAST = 0.2
ENCODE_UTF_8 = 'utf8'
NEW_ENTERING_NODE = 'HANDSHAKE_WITH_ENTERING_NODE'


class Handshaker(Observable):

    def __init__(self,
                 own_information: NodeInformation,
                 broadcast_address: NetAddress = DEFAULT_BROADCAST,
                 birthtime=time.time()):
        super(Handshaker, self).__init__()
        self.own_information = own_information
        self.broadcast_Address = broadcast_address
        self.birthtime = birthtime
        self.broadcast_thread = threading.Thread(target=self.__send_broadcast)
        self.collect_thread = threading.Thread(target=self.__collect_exist_nodes)
        self.running = False
        self.introduce_socket = None
        self.response_socket = None

    def start(self):
        self.running = True
        self.collect_thread.start()
        time.sleep(1)
        self.broadcast_thread.start()

    def end(self):
        self.running = False
        self.broadcast_thread.join()
        if self.response_socket is not None:
            try:
                self.response_socket.shutdown(SHUT_RDWR)
            except (error, OSError, ValueError):
                pass
            self.response_socket.close()
        self.collect_thread.join()

    def __send_broadcast(self):
        self.introduce_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.introduce_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.introduce_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.introduce_socket.settimeout(TIMEOUT_BROADCAST)
        message = self.own_information.to_json()
        self.introduce_socket.sendto(bytes(message, encoding=ENCODE_UTF_8),
                                     (self.broadcast_Address.ip_address, self.broadcast_Address.port))
        self.introduce_socket.close()

    def __collect_exist_nodes(self):
        self.response_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.response_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.response_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.response_socket.bind(('', self.broadcast_Address.port))
        while self.running:
            data, addr = self.response_socket.recvfrom(MESSAGE_LENGTH)
            if data != b'':
                threading.Thread(target=self.__add_node_info_and_send_own(data))
        self.response_socket.close()

    def __add_node_info_and_send_own(self, data):
        data = data.decode(encoding=ENCODE_UTF_8)
        node_information = node_information_from_json(data)
        self.notify(UpdateValue(NEW_ENTERING_NODE, node_information))
