from src.beans import NodeInformation
import queue

DEFAULT_MESSAGE = 'OK'


class MessageDict:

    def __init__(self):
        self.dict = dict()

    def get_next_message(self, nodeInformation: NodeInformation) -> str:
        if nodeInformation in self.dict.keys():
            if self.dict[nodeInformation].empty():
                return DEFAULT_MESSAGE
            else:
                return self.dict[nodeInformation].get()
        else:
            raise ValueError("Node information is not in dictionary. Please contact coder.")

    def add_message_for_node(self, message: str, node: NodeInformation):
        if node not in self.dict.keys():
            self.dict[node] = queue.Queue()
        self.dict[node].put(message)

    def add_message_for_nodes(self, message: str, nodes: [NodeInformation]):
        for node in nodes:
            self.add_message_for_node(message, node)

    def clear(self):
        self.dict.clear()
