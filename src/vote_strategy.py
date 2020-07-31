"""
Provides abstract template Strategy and two implementations for
handling incoming votes and calculate new wish_master.
"""
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
    Abstract class which provides the template for calculate new wish_master
    and notify observer (NodeManger)
    """

    def __init__(self, own_information: NodeInformation, message_dict: MessageDict):
        super().__init__()
        self.own_information = own_information
        self.message_dict = message_dict
        self.node_manager = None
        self.voting_dict = dict()
        self.lock = Lock()

    def calc_new_master(self, connected: SynchronizedSet, lost: SynchronizedSet,
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
        self.own_information.wish_master = voted_for
        self.lock.release()
        self.__remove_dead_votes_and_eval(connected, dispatched, lost)

    def vote_for(self, send_information, connected: SynchronizedSet, lost: SynchronizedSet,
                 dispatched: SynchronizedSet):
        """
        Handle incoming vote by adding vote to voting dict and calculate wish_master.
        :param send_information: Node who send vote
        :param voted_node: Node which was voted
        :param connected: Set of Nodes which are connected
        :param lost: Set of Nodes which are lost
        :param dispatched: Set of Nodes which are dispatched
        :return: None
        """
        his_wish_master = send_information.wish_master

        self.lock.acquire()
        self.voting_dict[send_information] = his_wish_master
        self.lock.release()
        self.__remove_dead_votes_and_eval(connected, dispatched, lost)

    def get_best_node(self, nodes: [NodeInformation]) -> NodeInformation:
        raise NotImplementedError("Warning: Used abstract class VoteStrategy")

    def __remove_dead_votes_and_eval(self, connected: SynchronizedSet,
                                     dispatched: SynchronizedSet,
                                     lost: SynchronizedSet):
        """
        Remove votes from disconnected instances to avoid dead votes
        then will call help methodcheck_if_all_voted_and_calc_master
                :param connected: Set of Nodes which are connected
        :param lost: Set of Nodes which are lost
        :param dispatched: Set of Nodes which are dispatched
        :return:
        """
        for node in lost:
            if node in self.voting_dict:
                self.voting_dict.pop(node)
        for node in dispatched:
            if node in self.voting_dict:
                self.voting_dict.pop(node)
        self.check_if_enough_votes_and_calc_master(connected)

    def check_if_enough_votes_and_calc_master(self, connected):

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
                    self.notify_vote(most_voted)
            else:
                self.notify_vote(most_voted)

    def notify_vote(self, most_voted):
        self.lock.acquire()
        self.notify(UpdateValue(NEW_MASTER, (self.node_manager.master, most_voted)))
        self.lock.release()


class PortStrategy(VoteStrategy):
    """
    Implementation of abstract class.
    """

    def get_best_node(self, nodes: [NodeInformation]) -> NodeInformation:
        """
        Select new wish_master by lowest number of PORT
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
        Select new wish_master by earliest time of initialisation
        :param nodes: all nodes in network
        :return: None
        """
        return sorted(nodes, key=lambda node: node.birthtime)[0]
