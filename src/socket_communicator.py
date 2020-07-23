import time
import socket
from src.flask_server import NetworkInformation
from multiprocessing import Process
from socket import AF_INET, SOCK_STREAM, IPPROTO_TCP, SOMAXCONN


class SocketCommunicator:

    def __init__(self, ownAddress : NetworkInformation):
        self.sock = socket.socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        self.sock.bind((ownAddress.ipAddress, ownAddress.port))
        self.sock.listen(SOMAXCONN)
        print ("Start socket at {}:{}".format(ownAddress.ipAddress, ownAddress.port))
        self.server_thread = Process(target=self.take_response)
        self.server_thread.start()

    def take_response(self):
        try:
            while True:
                inSocket, addr = self.sock.accept()
                thread = Process(target=self.start_ping_pong, args=(addr, inSocket))
                thread.start()
        finally:
            self.sock.close()

    def start_ping_pong(self, addr, inSocket):
        while True:
            print("Connection from {}".format(addr))
            msg = "Hello {0}, nice to meet you!\n".format(*socket.gethostbyname(addr[0]))
            inSocket.send(bytes(msg, 'utf-8'))
            self.sock.recv(1000)

    def connect_to(self, target : NetworkInformation):
        s = socket.socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        s.connect((target.ipAddress, target.port))
        while True:
            receivedBytes = s.recv(1000)
            if (len(receivedBytes) == 0):
                break
            print(receivedBytes.decode('utf-8'))
            s.send(bytes("Hello from connect_to\n", 'utf-8'))
        s.close()




if __name__ == '__main__':
    first = SocketCommunicator(NetworkInformation(port=8080))
    second = SocketCommunicator(NetworkInformation(port=5050))
    first.connect_to(NetworkInformation(port=5050))
