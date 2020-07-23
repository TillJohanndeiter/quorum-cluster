import json
import time

from flask import Flask
from multiprocessing import Process
from perfume import Perfume, route
from src.node_behavior import NodeStrategy, NormalStrategy


class NetworkInformation:

    def __init__(self, ip_address='0.0.0.0', port=8080):
        self.ipAddress = ip_address
        self.port = port


class NetworkInstance(Perfume):

    def __init__(self, ownAddress: NetworkInformation = None, masterAddress: NetworkInformation = None,
                 nodeStrategy: NodeStrategy = None):

        self.server_thread = Process(target=self.__start)
        self.app = Flask(__name__)
        self.startTime = time.time()
        self.ownAddress = ownAddress
        self.masterAddress = masterAddress
        self.nodeStrategy = nodeStrategy

    @route('/')
    def get_info(self):
        print(self.ownAddress)
        r = {
            'host': self.ownAddress.ipAddress,
            'port': self.ownAddress.port,
            'status': self.nodeStrategy.get_role(),
            'running': (time.time() - self.startTime)
        }
        return json.dumps(r)

    def start(self):
        NetworkInstance.register(self.app, route_base='/')
        self.server_thread.start()

    def end(self):
        self.server_thread.terminate()
        self.server_thread.join()

    def __start(self):
        return self.app.run(host=self.ownAddress.ipAddress, port=self.ownAddress.port)


class Node(NetworkInstance):

    def __init__(self, ownAddress: NetworkInformation, masterAddress: NetworkInformation,
                 nodeStrategy: NodeStrategy):
        super().__init__(ownAddress, masterAddress)
        self.nodeStrategy = nodeStrategy

    @route('/')
    def get_info(self):
        print(self.ownAddress)
        r = {
            'host': self.ownAddress.ipAddress,
            'port': self.ownAddress.port,
            'status': self.nodeStrategy.get_role(),
            'running': (time.time() - self.startTime)
        }
        return json.dumps(r)

    def start(self):
        Node.register(self.app, route_base='/')
        super(Node, self).start()


if __name__ == '__main__':
    ownAddress = NetworkInformation()
    # node = Node(ownAddress=ownAddress, masterAddress=ownAddress, nodeStrategy=NormalStrategy(ownAddress))
    node = NetworkInstance(ownAddress, ownAddress, NormalStrategy())
    node.run()