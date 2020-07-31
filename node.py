"""
Simple script to read arguments and create instance of node.
"""
import argparse
import os
from socket import socket, AF_INET, SOCK_STREAM

from src.factory import create_node_manger_by_node_info
from src.status_handler import StatusHandler
from src.beans import NodeInformation, NetAddress
from src.cmd_controller import CmdController

PORT_INFO = 'PORT in range of [1024...49151]'
ADDRESS_INFO = 'ADDRESS e.g localhost or subnet ADDRESS'

PARSER = argparse.ArgumentParser(description='Script to set up a node and ')
PARSER.add_argument('address',
                    help=ADDRESS_INFO, type=str,
                    default='0.0.0.0',
                    nargs='?')
PARSER.add_argument('port',
                    help=PORT_INFO,
                    type=int,
                    default=8080,
                    nargs='?')
PARSER.add_argument('broadcastAddress',
                    help=ADDRESS_INFO,
                    default='255.255.255.255',
                    type=str,
                    nargs='?')
PARSER.add_argument('broadcastPort',
                    help=PORT_INFO,
                    default=5595,
                    type=int,
                    nargs='?')
PARSER.add_argument('-n',
                    '--name',
                    help='optional NAME especially if you want to '
                         'understand the DEBUG log',
                    default=None,
                    type=str,
                    nargs='?')
PARSER.add_argument('--use_port_instead_of_life_time',
                    help='Use PORT instead of lifetime to determine quorum',
                    action='store_true')
PARSER.add_argument('-m', '--masterScript',
                    help='Python script that will be executed when node '
                         'become wish_master or keep wish_master status',
                    type=str,
                    default=None)
PARSER.add_argument('-s', '--slaveScript',
                    help='Python script that will be executed when '
                         'node become normal or keep normal status',
                    type=str,
                    default=None)
PARSER.add_argument('-d', '--debug', help='Print DEBUG messages while running',
                    action='store_true')


def port_in_use(host, port):
    """
    Check if port of host is closed
    :param host: target address
    :param port: port to check
    :return: True if open False if closed/used
    """
    sock = socket(AF_INET, SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0


if __name__ == '__main__':
    ARGS = PARSER.parse_args()
    ADDRESS = ARGS.address
    PORT = ARGS.port
    NAME = ARGS.name
    if NAME is None:
        NAME = 'Node with ADDRESS {} with PORT {}'.format(ADDRESS, PORT)

    if port_in_use(ADDRESS, PORT):
        for i in range(1024, 49151):
            if not port_in_use(host=ADDRESS, port=i):
                print('Port is already in use. Use free PORT {} instead of {}'.format(i, PORT))
                PORT = i
                break

    OWN_INFO = NodeInformation(NetAddress(ADDRESS, PORT), name=NAME)

    BROAD_INFO = NetAddress(ARGS.broadcastAddress, ARGS.broadcastPort)

    DEBUG = ARGS.debug

    if ARGS.use_port_instead_of_life_time is False:
        NODE_MANGER = create_node_manger_by_node_info(node_info=OWN_INFO,
                                                      broadcast_address=BROAD_INFO,
                                                      vote_by_port=False, debug=DEBUG,
                                                      human_user=True)
    else:
        NODE_MANGER = create_node_manger_by_node_info(node_info=OWN_INFO,
                                                      broadcast_address=BROAD_INFO,
                                                      vote_by_port=True, debug=DEBUG,
                                                      human_user=True)

    SLAVE_SCRIPT = ARGS.slaveScript

    if SLAVE_SCRIPT is not None:
        SLAVE_SCRIPT = os.path.abspath(SLAVE_SCRIPT)
        assert os.path.isfile(SLAVE_SCRIPT)

    MASTER_SCRIPT = ARGS.masterScript
    if MASTER_SCRIPT is not None:
        MASTER_SCRIPT = os.path.abspath(MASTER_SCRIPT)
        assert os.path.isfile(MASTER_SCRIPT)

    if MASTER_SCRIPT is not None or SLAVE_SCRIPT is not None:
        STATUS_HANDLER = StatusHandler(OWN_INFO, NODE_MANGER, SLAVE_SCRIPT, MASTER_SCRIPT)
        NODE_MANGER.vote_strategy.attach(STATUS_HANDLER)

    NODE_MANGER.start()
