class NodeStrategy:

    def get_role(self):
        raise NotImplementedError("Warning: Abstract class NetworkInstance has been used!")


class MasterStrategy(NodeStrategy):

    def get_role(self):
        return 'Master'


class NormalStrategy(NodeStrategy):

    def __init__(self, masterAddress = None):
        self.masterAddress = masterAddress

    def get_role(self):
        if self.masterAddress is None:
            return 'Masterless node'
        else:
            return 'Node from master: ' + self.masterAddress

