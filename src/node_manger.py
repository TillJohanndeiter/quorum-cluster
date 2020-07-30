import time

from collections import Counter
from synchronized_set import SynchronizedSet
from observer import Observer

from src.message_dict import MessageDict, DEFAULT_MESSAGE, DISPATCH_MESSAGE, \
    JSON_SEPARATOR, HANDSHAKE_MESSAGE, VOTE_MESSAGE, MESSAGE_SEPARATOR
from src.pinger import INCOMING_MESSAGE, CONNECTION_LOST, PingMan
from src.handshake import NEW_ENTERING_NODE, Handshaker
from src.beans import NodeInformation, node_information_from_json
from src.vote_strategy import VoteStrategy, NEW_MASTER, NO_MAJORITY_SHUTDOWN

TIME_BETWEEN_HANDSHAKE = 2


class NodeManger(Observer):

    def __init__(self, own_information: NodeInformation, ping_man: PingMan, handshaker: Handshaker,
                 message_dict: MessageDict, connected: SynchronizedSet, vote_strategy: VoteStrategy):
        super(NodeManger, self).__init__()
        self.own_information = own_information
        self.ping_man = ping_man
        self.handshaker = handshaker
        self.message_dict = message_dict
        self.connected = connected
        self.dispatched = SynchronizedSet(set())
        self.lost = SynchronizedSet(set())
        self.vote_strategy = vote_strategy
        self.vote_strategy.attach(self)
        self.master = None
        self.running = False

    def start(self):
        self.running = True
        time.sleep(TIME_BETWEEN_HANDSHAKE)
        self.ping_man.start()
        time.sleep(TIME_BETWEEN_HANDSHAKE)
        self.handshaker.start()
        self.vote_strategy.calc_new_master_and_add_message(self.connected, self.dispatched, self.lost)

    def kill(self):
        self.ping_man.kill()
        self.handshaker.kill()
        self.running = False

    def dispatch(self):
        self.handshaker.kill()
        self.message_dict.add_dispatch_message(self.own_information, self.connected)
        self.message_dict.wait_untill_everybody_received(self.own_dispatch_message())
        self.connected.clear()
        self.ping_man.kill()
        self.running = False

    def own_dispatch_message(self):
        return DISPATCH_MESSAGE + JSON_SEPARATOR + self.own_information.to_json()

    def update(self, update_value):
        update_value = update_value[0]
        event = update_value.name
        if event == NEW_ENTERING_NODE:
            self.__handle_entering_node(update_value)
        elif event == INCOMING_MESSAGE:
            self.__handle_messages(update_value)
        elif event == CONNECTION_LOST:
            self.__handle_connection_lost(update_value)
        elif event == NEW_MASTER:
            self.master = update_value.value
        elif event == NO_MAJORITY_SHUTDOWN:
            self.dispatch()

    def __handle_connection_lost(self, new_value):
        lost_node = new_value.value
        if lost_node in self.connected and lost_node not in self.dispatched:
            self.connected.remove(lost_node)
            self.lost.add(lost_node)
        if len(self.lost) > len(self.connected):
            print('{} dispatching because more lost than connected'.format(self.own_information.name))
            if self.running:
                self.dispatch()
        else:
            self.vote_strategy.calc_new_master_and_add_message(self.connected, self.dispatched, self.lost)
        self.message_dict.delete_message_for_node(lost_node)


    def __handle_messages(self, new_value):
        messages = str(new_value.value).split(MESSAGE_SEPARATOR)
        messages.sort(key=lambda x: x.startswith(HANDSHAKE_MESSAGE))
        for message in messages:
            self.__handle_non_default_message(message)

    def __handle_non_default_message(self, msg):
        subject = msg.split(JSON_SEPARATOR)[0]
        if subject == DEFAULT_MESSAGE:
            return

        json = msg.split(JSON_SEPARATOR)[1]
        node_info = node_information_from_json(json)
        if subject == DISPATCH_MESSAGE:
            print('{} Dispatched from {}'.format(self.own_information.name, node_info.name))
            if node_info in self.connected:
                self.connected.remove(node_info)
            if node_info in self.lost:
                self.lost.remove(node_info)
            self.dispatched.add(node_info)
            if len(self.lost) > len(self.connected):
                print('{} dispatching because more lost than connected'.format(self.own_information.name))
                if self.running:
                    self.dispatch()
            else:
                self.vote_strategy.calc_new_master_and_add_message(self.connected, self.dispatched, self.lost)
            self.message_dict.delete_message_for_node(node_info)
        elif subject == HANDSHAKE_MESSAGE:
            if node_info != self.own_information:
                self.message_dict.add_node(node_info)
                self.remove_node_from_dispatch_if_same_name(node_info)
                self.connected.add(node_info)
                print('{} add {} to connected len of connected {}'.format(self.own_information.name, node_info.name,
                                                                          len(self.connected)))
            if node_info in self.dispatched:
                self.dispatched.remove(node_info)
            if node_info in self.lost:
                self.lost.remove(node_info)
            self.vote_strategy.calc_new_master_and_add_message(self.connected, self.dispatched, self.lost)
        elif subject == VOTE_MESSAGE:
            voted_from = node_info
            json = msg.split(JSON_SEPARATOR)[2]
            voted_node = node_information_from_json(json)
            self.vote_strategy.vote_for(voted_from, voted_node, self.connected, self.dispatched, self.lost)

    def remove_node_from_dispatch_if_same_name(self, node_info):
        for old_node in self.dispatched.copy():
            if old_node.name == node_info.name and old_node in self.dispatched:
                self.dispatched.remove(old_node)

    def __handle_entering_node(self, new_value):
        node_info = new_value.value
        if node_info != self.own_information:
            self.message_dict.add_handshake_message(own=self.own_information, target=node_info)
            self.remove_node_from_dispatch_if_same_name(node_info)
            self.connected.add(node_info)
            self.vote_strategy.calc_new_master_and_add_message(self.connected, self.dispatched, self.lost)
