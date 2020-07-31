"""
Provides help method for better creation of instances in testing and cmd script.
"""

import time

import synchronized_set

from src.beans import NetAddress, NodeInformation
from src.cmd_controller import CmdController
from src.node_manger import NodeManger
from src.handshake import Handshake, DEFAULT_BROADCAST
from src.message_dict import MessageDict
from src.pinger import PingMan
from src.vote_strategy import TimeStrategy, PortStrategy


def create_node_manger(address: str, port: int, name=None) -> NodeManger:
    """
    Help method to create instance of NodeManger with observed instance of VoteStrategy and PingMan
    :param address: Address of Instance
    :param port: PORT of Instance
    :param name: Name of Instance
    :return: created Instance
    """
    address_info = NetAddress(host=address, port=port)
    node_info = NodeInformation(address_info, birthtime=time.time(), name=name)
    manager = create_node_manger_by_node_info(node_info)
    return manager


def create_node_manger_by_node_info(node_info: NodeInformation,
                                    broadcast_address=DEFAULT_BROADCAST,
                                    vote_by_port=False, debug=False, human_user=False) -> NodeManger:
    """
    Help method to create instance of NodeManger with observed instance of VoteStrategy and PingMan
    :param node_info: Info used for creation of instance
    :param broadcast_address: Broadcast Address for entering instances and making Handshake
    :param vote_by_port: Flag decides if master is calculated by PORT or birthtime of node
    :return: created NodeManger
    """
    message_dict = MessageDict(node_info)
    connected_set = synchronized_set.SynchronizedSet(set())
    handshake = Handshake(own_information=node_info, broadcast_address=broadcast_address)
    ping_man = PingMan(own_information=node_info,
                       message_dict=message_dict,
                       connected=connected_set)

    if vote_by_port:
        vote_strategy = PortStrategy(node_info, message_dict)
    else:
        vote_strategy = TimeStrategy(node_info, message_dict)

    manager = NodeManger(message_dict=message_dict, own_information=node_info,
                         connected=connected_set, ping_man=ping_man, handshaker=handshake,
                         vote_strategy=vote_strategy)
    handshake.attach(manager)
    ping_man.attach(manager)


    CMD_CONTROLLER = CmdController(manager, debug)
    manager.vote_strategy.attach(CMD_CONTROLLER)
    manager.ping_man.attach(CMD_CONTROLLER)
    manager.handshaker.attach(CMD_CONTROLLER)
    if human_user:
        CMD_CONTROLLER.start_input_loop()

    return manager
