from src.beans import NodeInformation


class VoteStrategy:

    def get_best_node(self, nodes: [NodeInformation]):
        raise NotImplementedError("Warning: Used abstract class VoteStrategy")


class PortStrategy(VoteStrategy):

    def get_best_node(self, nodes: [NodeInformation]):
        return sorted(nodes, key=lambda node: node.net_address.port)[0]


class TimeStrategy(VoteStrategy):

    def get_best_node(self, nodes: [NodeInformation]):
        return sorted(nodes, key=lambda node: node.birthtime)[0]
