from src.beans import NodeInformation
import queue
import synchronized_set
import time

DEFAULT_MESSAGE = 'OK'
DISPATCH_MESSAGE = 'BYE'
HANDSHAKE_MESSAGE = 'HANDSHAKE'

SEPARATOR = ':_:'


class MessageDict:

    def __init__(self):
        self.dict = dict()

    def get_next_message(self, nodeInformation: NodeInformation) -> str:
        if nodeInformation in self.dict.keys():
            if self.dict[nodeInformation].empty():
                return DEFAULT_MESSAGE + SEPARATOR
            else:
                return self.dict[nodeInformation].get()
        else:
            return DEFAULT_MESSAGE + SEPARATOR

    def add_message_for_node(self, message: str, target: NodeInformation):
        if target not in self.dict.keys():
            self.dict[target] = queue.Queue()
        self.dict[target].put(message)

    def add_message_for_all_nodes(self, message: str):
        for node in self.dict.keys():
            self.add_message_for_node(message, node)

    def add_node(self, node: NodeInformation):
        self.dict[node] = queue.Queue()

    def add_handshake_message(self, own: NodeInformation, target: NodeInformation):
        self.add_message_for_node(HANDSHAKE_MESSAGE + SEPARATOR + own.to_json(), target)

    def add_dispatch_message(self, own_information : NodeInformation, node_information: [synchronized_set.SynchronizedSet]):
        for target in node_information:
            self.add_message_for_node(DISPATCH_MESSAGE + SEPARATOR + own_information.to_json(), target)

    def wait_unit_everybody_received(self, message):
        while not self.check_if_all_get_message(message):
            time.sleep(1)
        time.sleep(5)
        print('All recieved: {} from'.format(message))

    def check_if_all_get_message(self, message):
        all_get_message = True
        for node in self.dict.keys():
            if message in self.dict[node].queue:
                all_get_message = False

        return all_get_message

    def clear(self):
        self.dict.clear()
