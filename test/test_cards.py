import unittest
from pokeher.cards import *
import pokeher.constants as C

class CardTest(unittest.TestCase):
    def test_card_slots(self):
        """Makes sure slots are active on Card"""
        try:
            c = Card(3, 3)
            c.extra = 'fail'
        except AttributeError:
            pass
        else:
            self.fail("slots didn't explode")

    def test_eq(self):
        """Tests the card equals function, and that we can make a full deck"""
        cards = []
        for i in range(0, 4):
            suit = i
            for j in range(2, 15):
                card1 = Card(j, suit)
                card2 = Card(j, suit)
                cards.append(card1)
                self.assertTrue(card1.is_pair(card2))
                self.assertTrue(card1.is_suited(card2))
                self.assertEqual(card1, card2)
        self.assertEqual(len(cards), 52)
        self.assertEqual(cards, list(Card.full_deck()))

    def test_one_suit(self):
        """Make sure one suit works correctly"""
        clubs = Card.one_suit(0)
        self.assertEqual(len(clubs), 13)

    def test_comparisons(self):
        """Tests that lt, lte, gt, gte all work on Card"""
        aceH = Card(C.ACE, C.HEARTS)
        aceS = Card(C.ACE, C.SPADES)
        threeC = Card(3, C.CLUBS)

        self.assertTrue(aceS > aceH)
        self.assertTrue(threeC < aceS)
        self.assertTrue(aceH >= threeC)
        self.assertTrue(aceH == aceH)
        self.assertFalse(aceH == aceS)

class HandTest(unittest.TestCase):
    aceH = Card(C.ACE, C.HEARTS)
    aceS = Card(C.ACE, C.SPADES)
    kingS = Card(C.KING, C.SPADES)
    jackD = Card(C.JACK, C.DIAMONDS)

    def test_constructor(self):
        """Tests properties of the hand constructor"""
        h = Hand(self.aceS, self.kingS)

        self.assertEqual(self.aceS, h.high)
        self.assertEqual(self.kingS, h.low)

        self.assertTrue(h.is_suited())
        self.assertTrue(h.is_connected())
        self.assertFalse(h.is_pair())

        h2 = Hand(Card(5, C.HEARTS), Card(7, C.HEARTS))
        self.assertTrue(h2.is_suited())
        self.assertFalse(h2.is_connected())
        self.assertFalse(h2.is_pair())

    def test_repr_string(self):
        h = Hand(self.jackD, self.aceS)

        self.assertEqual(repr(h), '143111')
        self.assertEqual(str(h), 'A-Spades, J-Diamonds')

    def test_hand_negs(self):
        """Tests an unsuited, unconnected hand"""
        h = Hand(self.aceH,self.jackD)

        self.assertEqual(self.aceH, h.high)
        self.assertEqual(self.jackD, h.low)

        self.assertFalse(h.is_suited())
        self.assertFalse(h.is_connected())
        self.assertFalse(h.is_pair())
        self.assertEqual(h.card_gap(), 2)

if __name__ == '__main__':
    unittest.main()
