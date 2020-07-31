"""
Provides abstract template Strategy and two implementations for
handling incoming votes and calculate new master.
"""
import time
from collections import Counter
from synchronized_set import SynchronizedSet
from threading import Lock
from observer import Observable
from src.beans import NodeInformation, UpdateValue
from src.message_dict import MessageDict

NEW_MASTER = 'NEW_MASTER'
VOTE_FOR = 'VOTE_FOR'
NO_MAJORITY_SHUTDOWN = 'NO_MAJORITY_SHUTDOWN'
SECONDS_WAIT_FOR_VOTES = 5


class VoteStrategy(Observable):
    """
    Abstract class which provides the template for calculate new master
    and notify observer (NodeManger)
    """

    def __init__(self, own_information: NodeInformation, message_dict: MessageDict):
        super().__init__()
        self.own_information = own_information
        self.message_dict = message_dict
        self.voting_dict = dict()
        self.lock = Lock()
        self.wait_for_votes = False

    def calc_new_master_and_add_message(self, connected: SynchronizedSet, lost: SynchronizedSet,
                                        dispatched: SynchronizedSet):
        """
        :param connected: set of currently connected nodes
        :param lost: set of currently lost node
        :param dispatched: set of currently dispatched nodes
        :return: None
        """
        all_nodes = SynchronizedSet({self.own_information}).union(connected)
        voted_for = self.get_best_node(all_nodes)
        self.lock.acquire()
        self.voting_dict[self.own_information] = voted_for
        self.own_information.master = voted_for
        self.lock.release()
        self.__eval_votes_and_make_new_master(connected, dispatched, lost)

    def vote_for(self, send_information, connected: SynchronizedSet, lost: SynchronizedSet,
                 dispatched: SynchronizedSet):
        """
        Handle incoming vote by adding vote to voting dict and calculate master.
        :param send_information: Node who send vote
        :param voted_node: Node which was voted
        :param connected: Set of Nodes which are connected
        :param lost: Set of Nodes which are lost
        :param dispatched: Set of Nodes which are dispatched
        :return: None
        """
        his_master = send_information.master

        self.lock.acquire()
        self.voting_dict[send_information] = his_master
        self.lock.release()
        self.__eval_votes_and_make_new_master(connected, dispatched, lost)

    def get_best_node(self, nodes: [NodeInformation]) -> NodeInformation:
        raise NotImplementedError("Warning: Used abstract class VoteStrategy")

    def __eval_votes_and_make_new_master(self, connected: SynchronizedSet,
                                         dispatched: SynchronizedSet,
                                         lost: SynchronizedSet):

        for node in lost:
            if node in self.voting_dict:
                self.voting_dict.pop(node)
        for node in dispatched:
            if node in self.voting_dict:
                self.voting_dict.pop(node)
        self.check_if_all_voted_and_calc_master(connected)

    def check_if_all_voted_and_calc_master(self, connected):

        if SynchronizedSet(list(self.voting_dict)).issuperset(connected):

            all_nodes = SynchronizedSet({self.own_information}).union(connected)
            voted_for = self.get_best_node(all_nodes)
            self.lock.acquire()
            self.voting_dict[self.own_information] = voted_for
            self.lock.release()

            occurrence_count = Counter(list(self.voting_dict.values()))
            most_voted = occurrence_count.most_common(1)[0][0]
            vote_count = occurrence_count.most_common(1)[0][1]

            if vote_count < len(all_nodes) / 2:

                if self.voting_dict[self.own_information] != most_voted:
                    self.notify(UpdateValue(NO_MAJORITY_SHUTDOWN))
                else:
                    self.update_if_master_changed(most_voted)
            else:
                self.update_if_master_changed(most_voted)

    def update_if_master_changed(self, most_voted):
        if most_voted != self.own_information.master:
            self.notify(UpdateValue(NEW_MASTER, most_voted))


class PortStrategy(VoteStrategy):
    """
    Implementation of abstract class.
    """

    def get_best_node(self, nodes: [NodeInformation]) -> NodeInformation:
        """
        Select new master by lowest number of PORT
        :param nodes: all nodes in network
        :return: None
        """
        return sorted(nodes, key=lambda node: node.net_address.port)[0]


class TimeStrategy(VoteStrategy):
    """
    Implementation of abstract class.
    """

    def get_best_node(self, nodes: [NodeInformation]) -> NodeInformation:
        """
        Select new master by earliest time of initialisation
        :param nodes: all nodes in network
        :return: None
        """
        return sorted(nodes, key=lambda node: node.birthtime)[0]
