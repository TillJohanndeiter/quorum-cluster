"""
Module provided a dataclass which is used as an dictionary to know what messages will be
send during next ping.
"""

import time
import threading
import queue
import synchronized_set

from src.beans import NodeInformation

DEFAULT_MESSAGE = 'OK'
DISPATCH_MESSAGE = 'BYE'
HANDSHAKE_MESSAGE = 'HANDSHAKE'
JSON_SEPARATOR = ':_:'
MESSAGE_SEPARATOR = '--__--'


class MessageDict:
    """
    Dataclass is used as dictionary to know what messages will be send during next ping.
    As an underlying data structure a dict which maps NodeInformation to a Queue of Strings is used
    As format for node information json is used.
    """

    def __init__(self, own_info : NodeInformation):
        self.dict = dict()
        self.lock = threading.Lock()
        self.own_info = own_info

    def get_next_message(self, node_information: NodeInformation) -> str:
        """
        Return concatenated messages in Queue. If Queue of node is empty default string
        with Ok and own information with master wish.
        :param node_information: node to which messages will be send
        :return: concatenated messages separated by MESSAGE_SEPARATOR or default string
        """
        if node_information in self.dict.keys():
            if self.dict[node_information].empty():
                return DEFAULT_MESSAGE + JSON_SEPARATOR + self.own_info.to_json()
            copy = list(self.dict[node_information].queue)
            with self.dict[node_information].mutex:
                self.dict[node_information].queue.clear()
            return MESSAGE_SEPARATOR.join(copy)
        return DEFAULT_MESSAGE + JSON_SEPARATOR + self.own_info.to_json()

    def add_message_for_node(self, message: str, target: NodeInformation):
        """
        Add message to queue. If entry for node doesn't exists.
        Method is thread safe.
        :param message: string that will be appended to queue
        :param target: node which should receive message
        :return: None
        """
        self.lock.acquire()
        if target not in self.dict.keys():
            self.dict[target] = queue.Queue()
        self.dict[target].put(message)
        self.lock.release()

    def add_message_for_all_nodes(self, message: str):
        """
        Add message to all nodes which are in dictionary
        :param message: string that will be appended to queue
        :return: None
        """
        for node in self.dict:
            self.add_message_for_node(message, node)

    def add_node(self, node: NodeInformation):
        """
        Initialize queue for a node in dictionary.
        :param node:
        :return: None
        """
        self.lock.acquire()
        if node not in self.dict.keys():
            self.dict[node] = queue.Queue()
        self.lock.release()

    def add_handshake_message(self, own: NodeInformation, target: NodeInformation):
        """
        Add Handshake message for target node in dictionary.
        :param own: own node information that will be send in handshake
        :param target: node which going to receive message
        :return: None
        """
        self.add_message_for_node(HANDSHAKE_MESSAGE + JSON_SEPARATOR + own.to_json(), target)

    def add_dispatch_message(self, own_information: NodeInformation,
                             node_information: synchronized_set.SynchronizedSet):
        """
        Add dispatch message for target node in dictionary.
        :param own: own node information that will be send in dispatch message
        :param node_information: nodes which going to receive message
        :return: None
        """
        for target in node_information:
            self.add_message_for_node(
                DISPATCH_MESSAGE + JSON_SEPARATOR + own_information.to_json(),
                target)

    def wait_until_everybody_received(self, message):
        """
        Will stuck in a loop as long as the message is in at least one queue.
        :param message: message that have to be send
        """
        while not self.check_if_all_get_message(message):
            time.sleep(1)
        time.sleep(3)

    def check_if_all_get_message(self, message):
        """
        Help method for wait_until_everybody_received
        :param message: message that have to be send
        :return: True if received else false
        """
        all_get_message = True
        for node in self.dict:
            if message in self.dict[node].queue:
                all_get_message = False

        return all_get_message

    def delete_message_for_node(self, node_info: NodeInformation):
        """
        Will delete all messages for one node in queue.
        :param node_info: node for which messages will be deleted
        :return: None
        """
        self.lock.acquire()
        if node_info in self.dict.keys():
            self.dict[node_info].queue.clear()
        self.lock.release()

    def clear(self):
        """
        Will delete all entries and keys in dict.
        :return: None
        """
        self.dict.clear()
