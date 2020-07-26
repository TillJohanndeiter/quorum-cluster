import synchronized_set

from observer import Observer
from src.beans import NodeInformation
from src.message_dict import MessageDict
from src.pinger import NEW_EXISTING_NODE, PingMan
from src.handshake import NEW_ENTERING_NODE


class NodeManger(Observer):

    def __init__(self, own_information : NodeInformation, ping_man: PingMan, message_dict : MessageDict):
        super(NodeManger, self).__init__()
        self.own_information = own_information
        self.ping_man = ping_man
        self.message_dict = message_dict
        self.connected = synchronized_set.SynchronizedSet(set())

    def update(self, new_value):
        new_value = new_value[0]
        id = new_value.name
        if id == NEW_ENTERING_NODE:
            node_info = new_value.value
            print('{} collected: {}'.format(self.own_information.name, node_info.name))
            if node_info != self.own_information:
                self.message_dict.add_message_for_node(self.own_information.to_json(), node_info)
                self.connected.add(node_info)
                self.ping_man.connected.add(node_info)
        elif id == NEW_EXISTING_NODE:
            node_info = new_value.value
            self.message_dict.add_node(node_info)
            self.connected.add(node_info)
            self.ping_man.connected.add(new_value.value)
            print(self.connected)
