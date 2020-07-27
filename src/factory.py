import time

import synchronized_set

from src.beans import NetAddress, NodeInformation
from src.connection_manger import NodeManger
from src.handshake import Handshaker
from src.message_dict import MessageDict
from src.pinger import PingMan


def create_node_manger(address : str, port : int, name=None) -> NodeManger:
    address_info = NetAddress(host=address, port=port)
    node_info = NodeInformation(address_info, birthtime=time.time(), name=name)
    manager = create_node_manger_by_node_info(node_info)
    return manager


def create_node_manger_by_node_info(node_info : NodeInformation) -> NodeManger:
    message_dict = MessageDict()
    connected_set = synchronized_set.SynchronizedSet(set())
    handshaker = Handshaker(own_information=node_info)
    pinger = PingMan(own_address=node_info, message_dict=message_dict, connected=connected_set)
    manager = NodeManger(message_dict=message_dict, own_information=node_info,
                         connected=connected_set, ping_man=pinger, handshaker=handshaker)
    handshaker.attach(manager)
    pinger.attach(manager)
    return manager