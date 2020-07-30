"""
Provides abstract template Strategy and two implementations for
handling incoming votes and calculate new master.
"""
from collections import Counter
from synchronized_set import SynchronizedSet
from observer import Observable

from src.beans import NodeInformation, UpdateValue
from src.message_dict import MessageDict

NEW_MASTER = 'NEW_MASTER'
VOTE_FOR = 'VOTE_FOR'
NO_MAJORITY_SHUTDOWN = 'NO_MAJORITY_SHUTDOWN'


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

    def calc_new_master_and_add_message(self, connected: SynchronizedSet, lost: SynchronizedSet,
                                        dispatched: SynchronizedSet):
        """
        :param connected: set of currently connected nodes
        :param lost: set of currently lost node
        :param dispatched: set of currently dispatched nodes
        :return: None
        """
        copy_connected = connected.copy()
        copy_connected.add(self.own_information)
        voted_for = self._get_best_node(copy_connected)
        self.notify(UpdateValue(VOTE_FOR, voted_for))
        self.message_dict.add_vote(voted_node=voted_for,
                                   own_info=self.own_information,
                                   node_information=connected)
        self.voting_dict[self.own_information] = voted_for
        self.__eval_votes_and_make_new_master(SynchronizedSet(copy_connected), dispatched, lost)

    def vote_for(self, voted_from, voted_node, connected: SynchronizedSet, lost: SynchronizedSet,
                 dispatched: SynchronizedSet):
        """
        Handle incoming vote by adding vote to voting dict and calculate master.
        :param voted_from: Node who send vote
        :param voted_node: Node which was voted
        :param connected: Set of Nodes which are connected
        :param lost: Set of Nodes which are lost
        :param dispatched: Set of Nodes which are dispatched
        :return: None
        """
        self.voting_dict[voted_from] = voted_node
        copy_connected = connected.copy()
        copy_connected.add(self.own_information)
        self.__eval_votes_and_make_new_master(SynchronizedSet(copy_connected), dispatched, lost)

    def _get_best_node(self, nodes: [NodeInformation]) -> NodeInformation:
        raise NotImplementedError("Warning: Used abstract class VoteStrategy")

    def __eval_votes_and_make_new_master(self, copy_connected: SynchronizedSet,
                                         dispatched: SynchronizedSet,
                                         lost: SynchronizedSet):

        for node in lost:
            if node in self.voting_dict:
                self.voting_dict.pop(node)
        for node in dispatched:
            if node in self.voting_dict:
                self.voting_dict.pop(node)

        if SynchronizedSet(self.voting_dict.keys()).issuperset(copy_connected):
            occurrence_count = Counter(list(self.voting_dict.values()))
            master = occurrence_count.most_common(1)[0][0]
            self.notify(UpdateValue(NEW_MASTER, master))
            if occurrence_count.most_common(1)[0][1] < len(copy_connected) / 2:
                self.notify(UpdateValue(NO_MAJORITY_SHUTDOWN))
            self.voting_dict.clear()


class PortStrategy(VoteStrategy):
    """
    Implementation of abstract class.
    """
    def _get_best_node(self, nodes: [NodeInformation]) -> NodeInformation:
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
    def _get_best_node(self, nodes: [NodeInformation]) -> NodeInformation:
        """
        Select new master by earliest time of initialisation
        :param nodes: all nodes in network
        :return: None
        """
        return sorted(nodes, key=lambda node: node.birthtime)[0]
