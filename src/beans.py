import json
import time

class NetAddress:
    def __init__(self, host='localhost', port=3030):
        self.host = host
        self.port = port

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_tuple(self):
        return self.host, self.port

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, NetAddress):
            return False
        return self.host == o.host and self.port == o.port

    def __hash__(self) -> int:
        return hash(self.host) + hash(self.port)


class NodeInformation:

    def __init__(self,
                 net_address: NetAddress,
                 birthtime=time.time(),
                 name=None):
        self.net_address = net_address
        self.birthtime = birthtime
        self.name = name

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, NodeInformation):
            return False
        return self.net_address == o.net_address \
               and self.birthtime == o.birthtime \
               and self.name == o.name

    def __hash__(self) -> int:
        return hash(self.net_address) + hash(self.birthtime) + hash(self.name)


def node_information_from_json(json_string) -> NodeInformation:
    node_info_dict = json.loads(json_string)
    net_address = NetAddress(**node_info_dict['net_address'])
    node_info_obj = NodeInformation(**node_info_dict)
    node_info_obj.net_address = net_address
    return node_info_obj


def net_address_information_from_json(json_string) -> NetAddress:
    net_address_dict = json.loads(json_string)
    net_address = NetAddress(**net_address_dict)
    return net_address
