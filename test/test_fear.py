import unittest

import pokeher.handscore as handscore
import pokeher.constants as C
from pokeher.fear import OpponentHandRangeFear
from test_brain import MockData

class HandRangeFearTest(unittest.TestCase):
    def setUp(self):
        self.data = MockData()
        self.data.pot = 100

    def test_handscore_check(self):
        fear = OpponentHandRangeFear(self.data, 0)
        self.assertEqual(fear.tier.name, "CHECK")
        score = handscore.HandScore(0)
        score.kicker = tuple([None] * 5)
        self.assertEqual(fear.minimum_handscore(), score)

    def test_handscore_big_raise(self):
        fear = OpponentHandRangeFear(self.data, 100)
        self.assertEqual(fear.tier.name, "BIG_RAISE")
        score = handscore.HandScore(1)
        score.kicker = tuple([C.QUEEN] * 5)
        self.assertEqual(fear.minimum_handscore(), score)
