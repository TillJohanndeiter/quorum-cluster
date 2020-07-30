import argparse
import os
from socket import socket, AF_INET, SOCK_STREAM

from src.factory import create_node_manger_by_node_info
from src.status_handler import StatusHandler
from src.beans import NodeInformation, NetAddress
from src.cmd_controller import CmdController

PORT_INFO = 'port in range of [1024...49151]'
ADDRESS_INFO = 'address e.g localhost or subnet address'

parser = argparse.ArgumentParser(description='Script to set up a node and ')
parser.add_argument('address', help=ADDRESS_INFO, type=str, default='0.0.0.0', nargs='?')
parser.add_argument('port', help=PORT_INFO, type=int, default=8080, nargs='?')
parser.add_argument('broadcastAddress', help=ADDRESS_INFO, default='255.255.255.255', type=str, nargs='?')
parser.add_argument('broadcastPort', help=PORT_INFO, default=5595, type=int, nargs='?')
parser.add_argument('-n', '--name', help='optional name especially if you want to understand the debug log',
                    default=None, type=str, nargs='?')
parser.add_argument('--use_port_instead_of_life_time', help='Use port instead of lifetime to determine quorum',
                    action='store_true')
parser.add_argument('-m', '--masterScript',
                    help='Python script that will be executed when node become master or keep master status',
                    type=str, default=None)
parser.add_argument('-s', '--slaveScript',
                    help='Python script that will be executed when node become normal or keep normal status',
                    type=str, default=None)
parser.add_argument('-d', '--debug', help='Print debug messages while running', action='store_true')

def port_in_use(host, port):
    sock = socket(AF_INET, SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0




if __name__ == '__main__':
    args = parser.parse_args()
    address = args.address
    port = args.port
    name = args.name
    if name is None:
        name = 'Node with address {} with port {}'.format(address, port)

    if port_in_use(address, port):
        for i in range(1024, 49151):
            if not port_in_use(host=address, port=i):
                print('Port is already in use. Use free port {} instead of {}'.format(i, port))
                port = i
                break

    node_information = NodeInformation(NetAddress(address, port), name=name)

    broadcast_address = NetAddress(args.broadcastAddress, args.broadcastPort)

    if args.use_port_instead_of_life_time is False:
        node_manger = create_node_manger_by_node_info(node_info=node_information,
                                                      broadcast_address=broadcast_address,
                                                      vote_by_port=False)
    else:
        node_manger = create_node_manger_by_node_info(node_info=node_information,
                                                      broadcast_address=broadcast_address,
                                                      vote_by_port=True)

    slave_script = args.slaveScript

    if slave_script is not None:
        slave_script = os.path.abspath(slave_script)
        assert os.path.isfile(slave_script)

    master_script = args.masterScript
    if master_script is not None:
        master_script = os.path.abspath(master_script)
        assert os.path.isfile(master_script)

    if master_script is not None or slave_script is not None:
        status_handler = StatusHandler(node_information, slave_script, master_script)
        node_manger.vote_strategy.attach(status_handler)

    debug = args.debug

    if debug:
        cmd_controller = CmdController(node_manger)
        node_manger.vote_strategy.attach(cmd_controller)
        node_manger.ping_man.attach(cmd_controller)
        node_manger.handshaker.attach(cmd_controller)

    node_manger.start()