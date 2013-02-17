import unittest
from arena.holdem import *

class MockHoldem(Holdem):
    """Mocks out mixin methods that would usually be defined"""
    count = 2

    def bot_count(self):
        return self.count

class HoldemTest(unittest.TestCase):
    def test_dealer(self):
        for i in range (2, 10):
            self.verify_dealer(i)

    def verify_dealer(self, players):
        h = MockHoldem()
        h.count = players
        hands_list, remainder = h.deal_hands()

        self.assertTrue(hands_list)
        self.assertEqual(len(hands_list), h.bot_count())
        self.assertEqual(len(remainder), 52 - h.bot_count() * h.hand_size())

        seen = [] # no duplicate cards among hands
        for hand in hands_list:
            self.assertEqual(len(hand), h.hand_size())
            for card in hand:
                self.assertFalse(card in remainder)
                self.assertFalse(card in seen)
                seen.append(card)

        self.assertTrue(len(seen), 52 - len(remainder))
