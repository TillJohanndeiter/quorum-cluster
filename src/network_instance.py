from flask import Flask
from flask_classful import FlaskView, route
from multiprocessing import Process


class NetworkInformation:

    def __init__(self, ip_address, port):
        self.host = ip_address
        self.port = port


class NetworkInstance(FlaskView):
    def __init__(self, address: NetworkInformation = None):
        self.app = Flask(__name__)
        self.address = address
        self.status = None

    @route('/address')
    def get_address(self):
        return self.address

    @route('/role')
    def get_role(self):
        raise NotImplementedError("Please Implement this method")

    @route('/')
    def get_hello(self):
        return 'hello'

    def start(self):
        self.server_thread = Process(target=self.__start)
        self.server_thread.start()

    def end(self):
        self.server_thread.terminate()
        self.server_thread.join()

    def __start(self):
        return self.app.run(host=self.address.host, port=self.address.port)


class VotingDisk(NetworkInstance):

    @route('/role')
    def get_role(self):
        return 'votingDisk'

    def start(self):
        print('Start VotingDisk')
        VotingDisk.register(self.app, route_base='/')
        super(VotingDisk, self).start()


class Client(NetworkInstance):
    @route('/role')
    def get_role(self):
        return 'client'

    def start(self):
        print('Start Client')
        Client.register(self.app, route_base='/')
        super(Client, self).start()
