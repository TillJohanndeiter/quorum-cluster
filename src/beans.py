import json
import time
from json.decoder import JSONDecodeError

class NetAddress:
    def __init__(self, ip_address='0.0.0.0', port=3030):
        self.ip_address = ip_address
        self.port = port

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_tuple(self):
        return (self.ip_address, self.port)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, NetAddress):
            return False
        return self.ip_address == o.ip_address and self.port == o.port

    def __hash__(self) -> int:
        return hash(self.ip_address) + hash(self.port)


class NodeInformation:

    def __init__(self,
                 net_address: NetAddress,
                 status,
                 birthtime=time.time(),
                 name=None):
        self.net_address = net_address
        self.status = status
        self.birthtime = birthtime
        self.name = name

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, NodeInformation):
            return False
        return self.net_address == o.net_address \
               and self.status == o.status \
               and self.birthtime == o.birthtime \
               and self.name == o.name

    def __hash__(self) -> int:
        return hash(self.net_address) + hash(self.status) + hash(self.birthtime) + hash(self.name)


def node_information_from_json(json_string) -> NodeInformation:
    try:
        node_info_dict = json.loads(json_string)
        net_address = NetAddress(**node_info_dict['net_address'])
        node_info_obj = NodeInformation(**node_info_dict)
        node_info_obj.net_address = net_address
        return node_info_obj
    except JSONDecodeError:
        print("Faulty Json: {}".format(json_string))


def net_address_information_from_json(json_string) -> NetAddress:
    net_address_dict = json.loads(json_string)
    net_address = NetAddress(**net_address_dict)
    return net_address
