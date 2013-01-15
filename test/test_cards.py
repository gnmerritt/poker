import unittest
from pokeher.cards import *
from pokeher.cards import Constants as C

class SuitTest(unittest.TestCase):

    def test_eq(self):
        """Makes two instances of each suit and makes sure they're equal"""
        for i in range(0, 3):
            suit1 = Suit(i)
            suit2 = Suit(i)
            self.assertEqual(suit1, suit2)

    def test_bad_suit_values(self):
        """Tests the range of the suit constructor"""
        for i in range(-1, 12, 5):
            try:
                Suit(i)
            except AssertionError:
                pass
            else:
                self.fail('Suit({value}) allowed'.format(value=i))

class CardTest(unittest.TestCase):

    def test_card_not_suit(self):
        """Tests that the card constructor requires a Suit"""
        try:
            Card(0, 0)
        except AssertionError:
            pass
        else:
            self.fail('Card with non-suit value allowed')

    def test_card_bad_values(self):
        """Tests the card constructor value checks"""
        suit = Suit(0)
        for i in [-1, 15, 232]:
            try:
                Card(i, suit)
            except AssertionError:
                pass
            else:
                self.fail('value {i} allowed'.format(i=i))

    def test_eq(self):
        """Tests the card equals function, and that we can make a full deck"""
        cards = 0
        for i in range(0, 4):
            suit = Suit(i)
            for j in range(2, 15):
                card1 = Card(j, suit)
                card2 = Card(j, suit)
                cards = cards + 1
                self.assertTrue(card1.is_pair(card2))
                self.assertTrue(card1.is_suited(card2))
                self.assertEqual(card1, card2)
        self.assertEqual(cards, 52)

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

    def test_hand_negs(self):
        """Tests an unsuited, unconnected hand"""
        h = Hand(self.aceH,self.jackD)

        self.assertEqual(self.aceH, h.high)
        self.assertEqual(self.jackD, h.low)

        self.assertFalse(h.is_suited())
        self.assertFalse(h.is_connected())
        self.assertFalse(h.is_pair())
        self.assertEqual(h.card_gap(), 2)

class HandBuilderTest(unittest.TestCase):
    cards1 = [Card(7, C.CLUBS),
              Card(8, C.CLUBS),
              Card(9, C.CLUBS),
              Card(10, C.CLUBS) ]
    cards2 = cards1 + [Card(6, C.CLUBS)]
    cards3 = cards1 + [Card(6, C.SPADES), Card(2, C.DIAMONDS), Card(C.ACE, C.HEARTS)]
    cards4 = cards3 + [Card(3, C.CLUBS)]

    def test_flush_finder_empty(self):
        """Tests that select_flush_suit degrades gracefully"""
        hb = HandBuilder([])
        self.assertEqual(None, hb.select_flush_suit())

        hb = HandBuilder(None)
        self.assertEqual(None, hb.select_flush_suit())

    def test_flush_finder(self):
        """Tests the flush finder"""
        hb = HandBuilder(self.cards1)
        self.assertFalse(hb.select_flush_suit())

        hb2 = HandBuilder(self.cards2)
        self.assertEqual(C.CLUBS.suit, hb2.select_flush_suit())

        hb3 = HandBuilder(self.cards3)
        self.assertFalse(hb3.select_flush_suit())

        hb4 = HandBuilder(self.cards4)
        self.assertEqual(C.CLUBS.suit, hb4.select_flush_suit())

    def test_score_hand_empty(self):
        """Tests that the HB doesn't explode for bad entries"""
        hb = HandBuilder([])
        self.assertEqual(HandBuilder.NO_SCORE, hb.score_hand())

        hb2 = HandBuilder(None)
        self.assertEqual(HandBuilder.NO_SCORE, hb2.score_hand())

    def test_score_hand_flush(self):
        """Tests finding flushes and straight flushes"""
        flush = self.cards1 + [Card(C.ACE, C.CLUBS)]
        hb_flush = HandBuilder(flush)
        self.assertEqual(HandBuilder.FLUSH, hb_flush.score_hand(), "didn't find flush")

        hb_s_flush = HandBuilder(self.cards2)
        self.assertEqual(HandBuilder.STRAIGHT_FLUSH, hb_s_flush.score_hand(), "didn't find straight flush")

    def test_score_hand_straight(self):
        """Tests finding a straight"""
        straight = self.cards1 + [Card(C.JACK, C.SPADES)]
        hb = HandBuilder(straight)
        print str(straight)
        self.assertEqual(HandBuilder.STRAIGHT, hb.score_hand(), "didn't score the straight")

if __name__ == '__main__':
    unittest.main()
