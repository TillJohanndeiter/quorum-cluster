import json
import time

from flask import Flask

from src.beans import NetAddress
from src.node_behavior import NormalStrategy

app = Flask(__name__)
startTime = time.time()
ownAddress = NetAddress()
masterAddress = NetAddress()
nodeStrategy = NormalStrategy()


@app.route('/')
def get_info():
    r = {
        'host': ownAddress.ip_address,
        'port': ownAddress.port,
        'status': nodeStrategy.get_role(),
        'running': (time.time() - startTime)
    }
    return json.dumps(r)


if __name__ == '__main__':
    app.run(host=ownAddress.ip_address, port=ownAddress.port)
