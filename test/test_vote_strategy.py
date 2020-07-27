import unittest

from src.vote_strategy import PortStrategy, TimeStrategy
from src.beans import NodeInformation, NetAddress

alice_information = NodeInformation(NetAddress(port=4040), birthtime=100, name='alice')
bob_information = NodeInformation(NetAddress(port=5050), birthtime=200, name='bob')
peter_information = NodeInformation(NetAddress(port=6060), birthtime= 50, name='peter')
all_information = [bob_information, alice_information, peter_information]


class VoteStrategyCase(unittest.TestCase):

    def test_port_strategy(self):
        port_strategy = PortStrategy()
        result = port_strategy.get_best_node(all_information)
        self.assertEqual(result, alice_information)

    def test_time_strategy(self):
        port_strategy = TimeStrategy()
        result = port_strategy.get_best_node(all_information)
        self.assertEqual(result, peter_information)


if __name__ == '__main__':
    unittest.main()
