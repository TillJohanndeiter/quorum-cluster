import argparse
import os
import sys
import ipaddress

sys.path.append('../')
from src.factory import create_node_manger_by_node_info
from src.status_handler import StatusHandler
from src.beans import NodeInformation, NetAddress

PORT_INFO = 'port in range of [1024...49151]'
ADDRESS_INFO = 'address e.g localhost or subnet address'

parser = argparse.ArgumentParser(description='Script to set up a node and ')
parser.add_argument('address', help=ADDRESS_INFO, type=str, default='0.0.0.0', nargs='?')
parser.add_argument('port', help=PORT_INFO, type=int, default=8080, nargs='?')
parser.add_argument('broadcastPort', help=PORT_INFO, default=1337, type=int, nargs='?')
parser.add_argument('name', help='optional ', default=None, type=str, nargs='?')
parser.add_argument('-q', '--quorum_by_vote', help='Use port instead of lifetime to determine quorum',
                    type=bool, default=False)
parser.add_argument('-m', '--masterScript',
                    help='Python script that will be executed when node become master or keep master status',
                    type=bool, default=None)
parser.add_argument('-s', '--slaveScript',
                    help='Python script that will be executed when node become normal or keep normal status',
                    type=bool, default=None)
parser.add_argument('-d', '--debug', help='Print debug log while running',
                    type=bool, default=False)

if __name__ == '__main__':
    args = parser.parse_args()
    address = args.address
    port = args.port
    name = args.name
    if name is None:
        name = 'Node with address {} with port {}'.format(address, port)

    node_information = NodeInformation(NetAddress(address, port), name=name)

    broadcast_addr = str(ipaddress.ip_interface(args.address).network.broadcast_address)

    broadcast_address = NetAddress(broadcast_addr, args.broadcastPort)

    slave_script = args.slaveScript

    if slave_script is not None:
        assert os.path.isfile(slave_script)
        slave_script = os.path.abspath(slave_script)

    master_script = args.masterScript
    if master_script is not None:
        assert os.path.isfile(master_script)
        master_script = os.path.abspath(master_script)

    if master_script is not None or slave_script is not None:
        status_handler = StatusHandler(node_information, slave_script, master_script)

    node_manger = create_node_manger_by_node_info(node_info=node_information, broadcast_address=broadcast_address)
    node_manger.start()
