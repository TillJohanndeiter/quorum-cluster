"""
Beans contains data classes used for better communication of addresses and information
regarding one node."""

import json
import time


class NetAddress:
    """
    Dataclass for host ADDRESS and PORT.
    """

    def __init__(self, host='0.0.0.0', port=3030):
        self.host = host
        self.port = port

    def to_json(self) -> str:
        """
        Convert instance to json string.
        :return: json string of instance
        """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_tuple(self):
        """
        Convert instance to tuple of host and PORT.
        :return: tuple of host and PORT
        """
        return self.host, self.port

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, NetAddress):
            return False
        return self.host == o.host and self.port == o.port

    def __hash__(self) -> int:
        return hash(self.host) + hash(self.port)


class NodeInformation:
    """
    Dataclass for information regarding one network node. Like ADDRESS, birthtime and NAME.
    """

    def __init__(self,
                 net_address: NetAddress,
                 birthtime=time.time(),
                 name=None):
        self.net_address = net_address
        self.birthtime = birthtime
        self.name = name

    def to_json(self) -> str:
        """
        Convert instance to tuple of host and PORT.
        :return: tuple of host and PORT
        """
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
    """
    Deserialized instance of NodeInformation.
    :param json_string: json String of an instance
    :return: Deserialized instance
    """
    node_info_dict = json.loads(json_string)
    net_address = NetAddress(**node_info_dict['net_address'])
    node_info_obj = NodeInformation(**node_info_dict)
    node_info_obj.net_address = net_address
    return node_info_obj


def net_address_information_from_json(json_string) -> NetAddress:
    """
     Deserialized instance of NetAddress.
     :param json_string: json String of an instance
     :return: Deserialized instance
     """
    net_address_dict = json.loads(json_string)
    net_address = NetAddress(**net_address_dict)
    return net_address

class UpdateValue:
    """
    Bean of transfer update values with NAME for identification what happened.
    """
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
