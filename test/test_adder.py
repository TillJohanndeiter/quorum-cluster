import unittest

from src.adder import Adder


class AdderCase(unittest.TestCase):
    def add(self):
        adder = Adder()
        self.assertEqual(adder.add(3, 5), 8)


if __name__ == '__main__':
    unittest.main()
