"""
Provides NodeManger which is responsible for events in network
"""
import time

from synchronized_set import SynchronizedSet
from observer import Observer

from src.message_dict import MessageDict, DEFAULT_MESSAGE, DISPATCH_MESSAGE, \
    JSON_SEPARATOR, HANDSHAKE_MESSAGE, MESSAGE_SEPARATOR
from src.pinger import INCOMING_MESSAGE, CONNECTION_LOST, PingMan
from src.handshake import NEW_ENTERING_NODE, Handshake
from src.beans import NodeInformation, node_information_from_json
from src.vote_strategy import VoteStrategy, NEW_MASTER, NO_MAJORITY_SHUTDOWN

TIME_BETWEEN_HANDSHAKE = 2


class NodeManger(Observer):
    """
    Handel any kind of events lost node, dispatching, reentering or dispatching
    """

    def __init__(self, own_information: NodeInformation,
                 ping_man: PingMan,
                 handshaker: Handshake,
                 message_dict: MessageDict,
                 connected: SynchronizedSet,
                 vote_strategy: VoteStrategy):
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

        """
        Start instance of PingMan and Handshake. After that it will calculate init
        wish_master.
        :return: None
        """
        self.vote_strategy.calc_new_master_and_add_message(self.connected, self.dispatched, self.lost)
        try:
            self.running = True
            time.sleep(TIME_BETWEEN_HANDSHAKE)
            self.ping_man.start()
            time.sleep(TIME_BETWEEN_HANDSHAKE)
            self.handshaker.start()
        except KeyboardInterrupt:
            pass

    def kill(self):
        """
        End PingMan and Handshake directly.
        :return: None
        """
        self.ping_man.kill()
        self.handshaker.kill()
        self.running = False

    def dispatch(self):
        """
        Will first end Handshake, then wait unit everybody received dispatch message
        and then end pingman to ensure that everybody know that shutdown was wanted.
        :return: None
        """
        self.running = False
        self.handshaker.kill()
        self.message_dict.add_dispatch_message(self.own_information, self.connected)
        self.message_dict.wait_until_everybody_received(self.__own_dispatch_message())
        self.connected.clear()
        self.ping_man.kill()

    def __own_dispatch_message(self):
        return DISPATCH_MESSAGE + JSON_SEPARATOR + self.own_information.to_json()

    def update(self, update_value):
        """
        Handle changes in the network by react to specific events
        from observed instances
        :param update_value: Notification about what happened
        :return: None
        """
        update_value = update_value[0]
        event = update_value.name
        if event == NEW_ENTERING_NODE:
            self.__handle_entering_node(update_value)
        elif event == INCOMING_MESSAGE:
            self.__handle_messages(update_value)
        elif event == CONNECTION_LOST:
            self.__handle_connection_lost(update_value)
        elif event == NEW_MASTER:
            self.master = update_value.value[1]
        elif event == NO_MAJORITY_SHUTDOWN:
            self.dispatch()

    def __handle_connection_lost(self, new_value):
        """
        React to lost connection by remove from connected if not dispatched and
        add to lost. If more lost than connect will init dispatching process.
        Otherwise will init start of new wish_master calculation
        :param new_value:
        :return:
        """
        lost_node = new_value.value
        self.message_dict.delete_message_for_node(lost_node)
        if lost_node in self.connected and lost_node not in self.dispatched:
            self.connected.remove(lost_node)
            self.lost.add(lost_node)

        if len(self.lost) > len(self.connected):
            print('{} dispatching because more lost than connected'.format(
                self.own_information.name))
            if self.running:
                self.dispatch()
        else:
            self.vote_strategy.calc_new_master_and_add_message(self.connected,
                                                               self.dispatched,
                                                               self.lost)

    def __handle_messages(self, new_value):
        """
        Will sort that handshakes will be handheld first to avoid missing
        information. Each message will be handled by __handle_message.
        :param new_value:
        :return:
        """
        messages = str(new_value.value).split(MESSAGE_SEPARATOR)
        messages.sort(key=lambda x: x.startswith(HANDSHAKE_MESSAGE))
        for message in messages:
            self.__handle_message(message)

    def __handle_message(self, msg):
        """
        React to different type of messages.
        :param msg: incoming messages
        :return: None
        """
        subject = msg.split(JSON_SEPARATOR)[0]
        if subject == DEFAULT_MESSAGE:
            json = msg.split(JSON_SEPARATOR)[1]
            node_info = node_information_from_json(json)
            self.vote_strategy.vote_for(node_info, self.connected,
                                        self.dispatched, self.lost)

        json = msg.split(JSON_SEPARATOR)[1]
        node_info = node_information_from_json(json)
        if subject == DISPATCH_MESSAGE:
            self.__handle_dispatch_msg(node_info)
            self.message_dict.delete_message_for_node(node_info)
        elif subject == HANDSHAKE_MESSAGE:
            self.__handle_handshake_message(node_info)

    def __handle_handshake_message(self, node_info):
        """
        Add Node to connected and remove old node form dispatched if
        new node has same name. After this will initiate calc of new wish_master.
        :param node_info: new node
        :return: None
        """
        if node_info != self.own_information:
            self.message_dict.add_node(node_info)
            self.__remove_node_from_dispatch_if_same_name(node_info)
            self.connected.add(node_info)
            #print('{} add {} to connected len of connected {}. Json {}'.format(self.own_information.name,
            #                                                          node_info.name,
            #                                                          len(self.connected), node_info.to_json()))
        if node_info in self.dispatched:
            self.dispatched.remove(node_info)
        if node_info in self.lost:
            self.lost.remove(node_info)
        self.vote_strategy.calc_new_master_and_add_message(self.connected,
                                                           self.dispatched,
                                                           self.lost)

    def __handle_dispatch_msg(self, node_info):
        """
        Remove node from lost or connected and add to dispatch. Will also initiate calculation of new wish_master
        :param node_info: dispatching node
        :return: None
        """
        print('{} Dispatched from {}'.format(self.own_information.name, node_info.name))
        if node_info in self.connected:
            self.connected.remove(node_info)
        if node_info in self.lost:
            self.lost.remove(node_info)
        self.dispatched.add(node_info)
        if len(self.lost) > len(self.connected):
            print('{} dispatching because more lost than connected'.format(
                self.own_information.name))
            if self.running:
                self.dispatch()
        else:
            self.vote_strategy.calc_new_master_and_add_message(self.connected,
                                                               self.dispatched,
                                                               self.lost)

    def __remove_node_from_dispatch_if_same_name(self, node_info):
        """
        Check if entering node has same name as dispatched node and will
        delete if both has same name.
        :param node_info: node to check
        :return: None
        """
        for old_node in self.dispatched.copy():
            if old_node.name == node_info.name and old_node in self.dispatched:
                self.dispatched.remove(old_node)

    def __handle_entering_node(self, new_value):
        """
        Will add new node to connected, add handshake in message dict for new node and
        initiate calculation of new wish_master
        :param new_value: update with node
        :return: None
        """
        node_info = new_value.value
        if node_info != self.own_information:
            self.message_dict.add_handshake_message(own=self.own_information, target=node_info)
            self.__remove_node_from_dispatch_if_same_name(node_info)
            self.connected.add(node_info)
            self.vote_strategy.calc_new_master_and_add_message(self.connected,
                                                               self.dispatched,
                                                               self.lost)
