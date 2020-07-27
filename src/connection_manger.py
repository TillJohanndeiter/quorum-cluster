import synchronized_set
import time

from observer import Observer
from src.message_dict import MessageDict, DEFAULT_MESSAGE, DISPATCH_MESSAGE, SEPARATOR, HANDSHAKE_MESSAGE
from src.pinger import INCOMING_MESSAGE, CONNECTION_LOST, PingMan
from src.handshake import NEW_ENTERING_NODE, Handshaker
from src.beans import NodeInformation, node_information_from_json

TIME_BETWEEN_HANDSHAKE = 2


class NodeManger(Observer):

    def __init__(self, own_information: NodeInformation, ping_man: PingMan, handshaker: Handshaker,
                 message_dict: MessageDict, connected: synchronized_set.SynchronizedSet):
        super(NodeManger, self).__init__()
        self.own_information = own_information
        self.ping_man = ping_man
        self.handshaker = handshaker
        self.message_dict = message_dict
        self.connected = connected
        self.dispatched = synchronized_set.SynchronizedSet(set())
        self.lost = synchronized_set.SynchronizedSet(set())

    def start(self):
        self.ping_man.start()
        time.sleep(TIME_BETWEEN_HANDSHAKE)
        self.handshaker.start()

    def kill(self):
        self.ping_man.kill()
        self.handshaker.kill()

    def dispatch(self):
        self.handshaker.kill()
        self.message_dict.add_dispatch_message(self.own_information, self.connected)
        self.message_dict.wait_unit_everybody_received(DISPATCH_MESSAGE + SEPARATOR + self.own_information.to_json())
        self.connected.clear()
        self.ping_man.kill()

    def update(self, new_value):
        new_value = new_value[0]
        event = new_value.name
        if event == NEW_ENTERING_NODE:
            self.__handle_entering_node(new_value)
        elif event == INCOMING_MESSAGE:
            self.__handle_message(new_value)
        elif event == CONNECTION_LOST:
            lost_node = new_value.value
            print('{} lost connection from {}'.format(self.own_information.name, lost_node.name))

            if lost_node in self.connected and lost_node not in self.dispatched:
                self.connected.remove(lost_node)
                self.lost.add(lost_node)

    def __handle_message(self, new_value):

        msg = str(new_value.value)
        type = msg.split(SEPARATOR)[0]

        if type == DEFAULT_MESSAGE:
            return

        node_info = node_information_from_json(msg.split(SEPARATOR)[1])

        if type == DISPATCH_MESSAGE:
            print('{} Dispatched from {}'.format(self.own_information.name, node_info.name))
            if node_info in self.connected:
                self.connected.remove(node_info)
            if node_info in self.lost:
                self.lost.remove(node_info)
            self.dispatched.add(node_info)
        elif type == HANDSHAKE_MESSAGE:
            if node_info != self.own_information:
                print('{} add {} to connected'.format(self.own_information.name, node_info.name))
                self.message_dict.add_node(node_info)
                self.connected.add(node_info)
            if node_info in self.dispatched:
                self.dispatched.remove(node_info)
            if node_info in self.lost:
                self.lost.remove(node_info)

    def __handle_entering_node(self, new_value):
        node_info = new_value.value
        if node_info != self.own_information:
            self.message_dict.add_handshake_message(own=self.own_information, target=node_info)
            # print('{} add handshake massge for {} to connected'.format(self.own_information.name, node_info.name))
            self.connected.add(node_info)
