import unittest
from pokeher.chen import *
from pokeher.cards import *
from pokeher.cards import Constants as C

class ChenScoreTest(unittest.TestCase):

    def test_pair(self):
        """Tests that pairs are scored correctly"""

        twotwo = Hand(Card(2, C.HEARTS), Card(2, C.SPADES))

        self.assertTrue(twotwo.is_pair())
        self.assertEquals(ChenScore(twotwo).score(), 5)

        JJ = Hand(Card(C.JACK, C.DIAMONDS), Card(C.JACK, C.CLUBS))

        self.assertTrue(JJ.is_pair())
        self.assertEquals(ChenScore(JJ).score(), 12)

    def test_suited(self):
        """Tests that suited cards get a bonus"""
        AK = Hand(Card(C.ACE, C.SPADES), Card(C.KING, C.SPADES))
        self.assertEquals(ChenScore(AK).score(), 12)

    def test_gap_and_under_q(self):
        """Tests that 5-7H is scored correctly"""
        five_seven = Hand(Card(5, C.HEARTS), Card(7, C.HEARTS))
        self.assertEquals(ChenScore(five_seven).score(), 6)

    def test_negative_score(self):
        """Tests that negative scores are reported correctly"""
        two_seven = Hand(Card(2, C.CLUBS), Card(7, C.HEARTS))
        self.assertEquals(ChenScore(two_seven).score(), -1)

if __name__ == '__main__':
    unittest.main()
