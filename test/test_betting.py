import unittest
from arena.betting import Blinds, NoBetLimit

class NoBetLimitTest(unittest.TestCase):
    def test_bets(self):
        """Makes sure all positive bets are allowed in no limit"""
        limit = NoBetLimit()
        pot = 100
        self.assertTrue(limit.check_bet(pot, 30))
        self.assertTrue(limit.check_bet(pot, 100*pot))
        self.assertFalse(limit.check_bet(pot, -30))

class BlindsTest(unittest.TestCase):
    def test_preconditions(self):
        try:
            blinds = Blinds(20, 10)
        except AssertionError:
            pass
        else:
            self.fail("allowed big blind to be smaller")

    def test_blinds_printer(self):
        """Tests that the blinds are printed correctly"""
        blinds = Blinds(10, 20)
        hand_print = set(blinds.hand_blinds())
        self.assertTrue("Match smallBlind 10" in hand_print)
        self.assertTrue("Match bigBlind 20" in hand_print)
