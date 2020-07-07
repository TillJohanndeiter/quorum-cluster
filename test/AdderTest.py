import unittest

from domain.Adder import Adder


class MyTestCase(unittest.TestCase):
    def test_something(self):
        adder = Adder()
        self.assertEqual(adder.add(3,5), 8)


if __name__ == '__main__':
    unittest.main()
