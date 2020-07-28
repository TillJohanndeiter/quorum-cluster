import time
import threading
import queue
import synchronized_set

from src.beans import NodeInformation

DEFAULT_MESSAGE = 'OK'
DISPATCH_MESSAGE = 'BYE'
HANDSHAKE_MESSAGE = 'HANDSHAKE'
VOTE_MESSAGE = 'VOTE'
JSON_SEPARATOR = ':_:'
MESSAGE_SEPARATOR = '--__--'


class MessageDict:

    def __init__(self):
        self.dict = dict()
        self.lock = threading.Lock()

    def get_next_message(self, node_information: NodeInformation) -> str:
        if node_information in self.dict.keys():
            if self.dict[node_information].empty():
                return DEFAULT_MESSAGE + JSON_SEPARATOR
            copy = list(self.dict[node_information].queue)
            with self.dict[node_information].mutex:
                self.dict[node_information].queue.clear()
            return MESSAGE_SEPARATOR.join(copy)
        return DEFAULT_MESSAGE + JSON_SEPARATOR

    def add_message_for_node(self, message: str, target: NodeInformation):
        self.lock.acquire()
        if target not in self.dict.keys():
            self.dict[target] = queue.Queue()
        self.dict[target].put(message)
        self.lock.release()

    def add_message_for_all_nodes(self, message: str):
        for node in self.dict.keys():
            self.add_message_for_node(message, node)

    def add_node(self, node: NodeInformation):
        self.dict[node] = queue.Queue()

    def add_handshake_message(self, own: NodeInformation, target: NodeInformation):
        self.add_message_for_node(HANDSHAKE_MESSAGE + JSON_SEPARATOR + own.to_json(), target)

    def add_dispatch_message(self, own_information: NodeInformation,
                             node_information: synchronized_set.SynchronizedSet):
        for target in node_information:
            self.add_message_for_node(
                DISPATCH_MESSAGE + JSON_SEPARATOR + own_information.to_json(),
                target)

    def wait_unit_everybody_received(self, message):
        while not self.check_if_all_get_message(message):
            time.sleep(1)
        time.sleep(3)

    def check_if_all_get_message(self, message):
        all_get_message = True
        for node in self.dict.keys():
            if message in self.dict[node].queue:
                all_get_message = False

        return all_get_message

    def add_vote(self, voted_node: NodeInformation, own_info: NodeInformation,
                 node_information: synchronized_set.SynchronizedSet):
        for target in node_information:
            self.add_message_for_node(VOTE_MESSAGE + JSON_SEPARATOR
                                      + own_info.to_json() + JSON_SEPARATOR + voted_node.to_json(),
                                      target)

    def clear(self):
        self.dict.clear()
