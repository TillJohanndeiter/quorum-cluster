import time

from collections import Counter
from synchronized_set import SynchronizedSet
from observer import Observer

from src.message_dict import MessageDict, DEFAULT_MESSAGE, DISPATCH_MESSAGE, \
    JSON_SEPARATOR, HANDSHAKE_MESSAGE, VOTE_MESSAGE, MESSAGE_SEPARATOR
from src.pinger import INCOMING_MESSAGE, CONNECTION_LOST, PingMan
from src.handshake import NEW_ENTERING_NODE, Handshaker
from src.beans import NodeInformation, node_information_from_json
from src.vote_strategy import TimeStrategy

TIME_BETWEEN_HANDSHAKE = 2


# TODO: Move voting actions to own class

class NodeManger(Observer):

    def __init__(self, own_information: NodeInformation, ping_man: PingMan, handshaker: Handshaker,
                 message_dict: MessageDict, connected: SynchronizedSet):
        super(NodeManger, self).__init__()
        self.own_information = own_information
        self.ping_man = ping_man
        self.handshaker = handshaker
        self.message_dict = message_dict
        self.connected = connected
        self.dispatched = SynchronizedSet(set())
        self.lost = SynchronizedSet(set())
        self.vote_strategy = TimeStrategy()
        self.master = None
        self.voting_dict = dict()
        self.running = False

    def start(self):
        self.running = True
        self.ping_man.start()
        time.sleep(TIME_BETWEEN_HANDSHAKE)
        self.handshaker.start()
        self.calc_new_master_and_add_message()

    def kill(self):
        self.ping_man.kill()
        self.handshaker.kill()
        self.running = False

    def dispatch(self):
        self.handshaker.kill()
        self.message_dict.add_dispatch_message(self.own_information, self.connected)
        self.message_dict.wait_unit_everybody_received(self.own_dispatch_message())
        self.connected.clear()
        self.ping_man.kill()
        self.running = False

    def own_dispatch_message(self):
        return DISPATCH_MESSAGE + JSON_SEPARATOR + self.own_information.to_json()

    def update(self, new_value):
        new_value = new_value[0]
        event = new_value.name
        if event == NEW_ENTERING_NODE:
            self.__handle_entering_node(new_value)
        elif event == INCOMING_MESSAGE:
            self.__handle_messages(new_value)
        elif event == CONNECTION_LOST:
            lost_node = new_value.value
            print('{} lost connection from {}'.format(self.own_information.name, lost_node.name))

            if lost_node in self.connected and lost_node not in self.dispatched:
                self.connected.remove(lost_node)
                self.lost.add(lost_node)

            if lost_node == self.master:
                self.calc_new_master_and_add_message()

            if len(self.lost) > len(self.connected):
                print('{} dispatching because more lost than connected'.format(self.own_information.name))
                self.dispatch()

    def calc_new_master_and_add_message(self):
        copy = self.connected.copy()
        copy.add(self.own_information)
        voted_for = self.vote_strategy.get_best_node(copy)
        print('{} want {} as new master'.format(self.own_information.name, voted_for.name))
        self.message_dict.add_vote(voted_node=voted_for,
                                   own_info=self.own_information,
                                   node_information=self.connected)
        self.voting_dict[self.own_information] = voted_for
        self.eval_votes_and_make_new_master(copy)

    def __handle_messages(self, new_value):
        messages = str(new_value.value).split(MESSAGE_SEPARATOR)
        messages.sort(key=lambda x: x.startswith(HANDSHAKE_MESSAGE))
        for message in messages:
            self.handle_non_default_message(message)

    def handle_non_default_message(self, msg):
        subject = msg.split(JSON_SEPARATOR)[0]
        if subject == DEFAULT_MESSAGE:
            return
        json = None
        try:
            json = msg.split(JSON_SEPARATOR)[1]
        except:
            print('Faulty Message : {}'.format(msg))
        node_info = node_information_from_json(json)
        if subject == DISPATCH_MESSAGE:
            print('{} Dispatched from {}'.format(self.own_information.name, node_info.name))
            if node_info in self.connected:
                self.connected.remove(node_info)
            if node_info in self.lost:
                self.lost.remove(node_info)
            self.dispatched.add(node_info)
            self.calc_new_master_and_add_message()
        elif subject == HANDSHAKE_MESSAGE:
            if node_info != self.own_information:
                self.message_dict.add_node(node_info)
                self.connected.add(node_info)
                print('{} add {} to connected len of connected {}'.format(self.own_information.name, node_info.name,
                                                                          len(self.connected)))
            if node_info in self.dispatched:
                self.dispatched.remove(node_info)
            if node_info in self.lost:
                self.lost.remove(node_info)
            self.calc_new_master_and_add_message()
        elif subject == VOTE_MESSAGE:
            voted_from = node_info
            json = msg.split(JSON_SEPARATOR)[2]
            voted_node = node_information_from_json(json)
            print(
                '{} get vote from {} voted for {}'.format(self.own_information.name, voted_from.name, voted_node.name))
            self.voting_dict[voted_from] = voted_node
            copy_connected = self.connected.copy()
            copy_connected.add(self.own_information)
            self.eval_votes_and_make_new_master(copy_connected)

    def eval_votes_and_make_new_master(self, copy_connected):

        for node in self.lost:
            if node in self.voting_dict:
                self.voting_dict.pop(node)
        for node in self.dispatched:
            if node in self.voting_dict:
                self.voting_dict.pop(node)

        if SynchronizedSet(self.voting_dict.keys()).issuperset(copy_connected):
            occurrence_count = Counter(list(self.voting_dict.values()))
            self.master = occurrence_count.most_common(1)[0][0]
            print('{} has master {}'.format(self.own_information.name, self.master.name))
            if occurrence_count.most_common(1)[0][1] < len(self.connected) / 2:
                print('{} dispatching their is not majority'.format(self.own_information.name))
                self.dispatch()
            self.voting_dict.clear()

    def __handle_entering_node(self, new_value):
        node_info = new_value.value
        if node_info != self.own_information:
            self.message_dict.add_handshake_message(own=self.own_information, target=node_info)
            self.connected.add(node_info)
            print('{} add {} to connected len of connected {}'.format(self.own_information.name, node_info.name,
                                                                      len(self.connected)))
            self.calc_new_master_and_add_message()
