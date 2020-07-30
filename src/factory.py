import time

import synchronized_set

from src.beans import NetAddress, NodeInformation
from src.node_manger import NodeManger
from src.handshake import Handshaker, DEFAULT_BROADCAST
from src.message_dict import MessageDict
from src.pinger import PingMan
from src.vote_strategy import TimeStrategy, PortStrategy


def create_node_manger(address: str, port: int, name=None) -> NodeManger:
    address_info = NetAddress(host=address, port=port)
    node_info = NodeInformation(address_info, birthtime=time.time(), name=name)
    manager = create_node_manger_by_node_info(node_info)
    return manager


def create_node_manger_by_node_info(node_info: NodeInformation,
                                    broadcast_address=DEFAULT_BROADCAST, vote_by_port=False) -> NodeManger:
    message_dict = MessageDict()
    connected_set = synchronized_set.SynchronizedSet(set())
    handshake = Handshaker(own_information=node_info, broadcast_address=broadcast_address)
    ping_man = PingMan(own_information=node_info, message_dict=message_dict, connected=connected_set)

    if vote_by_port:
        vote_strategy = PortStrategy(node_info, message_dict)
    else:
        vote_strategy = TimeStrategy(node_info, message_dict)

    manager = NodeManger(message_dict=message_dict, own_information=node_info,
                         connected=connected_set, ping_man=ping_man, handshaker=handshake,
                         vote_strategy=vote_strategy)
    handshake.attach(manager)
    ping_man.attach(manager)
    return manager
