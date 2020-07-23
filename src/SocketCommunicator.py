import socket
import time
from multiprocessing import Process
import multitimer
import threading
import queue


from src.flask_server import NetAddressInformation
from collections import deque

TIME_TO_SEND_DISPATCH_MESSAGE = 10
MAX_PING_TRY = 5
SECOND_INTERVAL_PING_TRY = 0.5
OK_RESPONSE = 'OK'
DISPATCH_MESSAGE = 'BYE'

# TODO: Handshake per broadcast!


class SocketCommunicator:

    def __init__(self, ownAddress: NetAddressInformation, connected=None,
                 failed=None, sucDisconnected=None):
        if sucDisconnected is None:
            sucDisconnected = []
        if failed is None:
            failed = []
        if connected is None:
            connected = []
        self.connected = connected
        self.failed = failed
        self.sucDisconnected = sucDisconnected
        self.ownAddress = ownAddress
        self.server_socket_thread = Process(target=self.__start_server_socket)
        self.pingTimer = multitimer.MultiTimer(interval=10, function=self.__send_ping_to_all, runonstart=True)
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.messageList = queue.Queue()
        self.sentToList = set()

    def start(self):
        self.server_socket_thread.start()
        self.pingTimer.start()

    def kill(self):
        self.server_socket_thread.kill()
        self.serverSocket.close()
        self.pingTimer.stop()

    def dispatch_from_network(self):
        self.pingTimer.stop()
        self.messageList.put(DISPATCH_MESSAGE)
        time.sleep(TIME_TO_SEND_DISPATCH_MESSAGE)


    def __set_up_server_socket(self):
        ipAddress = self.ownAddress.ipAddress
        port = self.ownAddress.port
        self.serverSocket.bind((ipAddress, port))
        self.serverSocket.listen(socket.SOMAXCONN)
        #print("Start serverSocket at {}:{}".format(ipAddress, port))
        try:
            while True:
                inSocket, addr = self.serverSocket.accept()
                print("Connection from {}".format(addr))
                if self.messageList.qsize() == 0:
                    msg = OK_RESPONSE
                    inSocket.send(bytes(msg, 'utf-8'))
                    inSocket.close()
                else:
                    msg = self.messageList.get()
                    inSocket.sendmsg(msg)
                    inSocket.close()
                    self.sentToList.add(addr)
                    if len(self.sentToList) >= self.connected:
                        self.sentToList = set()
                    else:
                        temp = self.sentToList.queue
                        temp[-1] = msg
                        self.sentToList = queue.Queue(self.sentToList.queue)


        finally:
            print('end server socket')
            self.serverSocket.close()

    def __send_ping_to_target(self, targetAddress: NetAddressInformation):
        global s
        pingCounter = 0
        sucConnected = False
        while pingCounter < MAX_PING_TRY and not sucConnected:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
                s.connect((targetAddress.ipAddress, targetAddress.port))
                """
                # get information about connection
                local = s.getsockname()
                remote = s.getpeername()
                print("{}:{} -> {}:{}".format(local[0], local[1], remote[0], remote[1]))
                """
                while True:
                    receivedBytes = s.recv(1000)
                    if len(receivedBytes) == 0:
                        break
                    message = receivedBytes.decode('utf-8')
                    if message == OK_RESPONSE:
                        sucConnected = True
                    elif message == DISPATCH_MESSAGE:
                        sucConnected = True
                        #TODO: Dispatching. But this requires handshake to avoid form ports caused by ide

            except:
                pingCounter += 1
                time.sleep(SECOND_INTERVAL_PING_TRY)
            finally:
                s.close()
        # close connection

        if pingCounter == MAX_PING_TRY:
            self.connected.remove(targetAddress)
            self.failed.append(targetAddress)

        s.close()

    def __send_ping_to_all(self):
        for target in self.connected:
            t = threading.Thread(target=self.__send_ping_to_target, args=(target,))
            t.start()

    def __start_server_socket(self):
        return self.__set_up_server_socket()
