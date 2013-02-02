import unittest
from pokeher.utility import *

class MathUtilsTest(unittest.TestCase):

    def test_percentage(self):
        self.assertEqual(MathUtils.percentage(5, 10), 50)
        self.assertEqual(MathUtils.percentage(20, 200), 10)
        self.assertEqual(MathUtils.percentage(0, 300), 0)
        self.assertEqual(MathUtils.percentage(300, 0), 0)
