import json
import time

from flask import Flask
from src.node_behavior import NormalStrategy


class NetworkInformation:
    def __init__(self, ip_address='0.0.0.0', port=3030):
        self.ipAddress = ip_address
        self.port = port


app = Flask(__name__)
startTime = time.time()
ownAddress = NetworkInformation()
masterAddress = NetworkInformation()
nodeStrategy = NormalStrategy()
nodeCommunicator = None
server_thread = None


@app.route('/')
def get_info():
    r = {
        'host': ownAddress.ipAddress,
        'port': ownAddress.port,
        'status': nodeStrategy.get_role(),
        'running': (time.time() - startTime)
    }
    return json.dumps(r)



if __name__ == '__main__':
    app.run(host=ownAddress.ipAddress, port=ownAddress.port)