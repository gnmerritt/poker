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
        high_card = Card(C.ACE, C.CLUBS)
        flush = self.cards1 + [high_card]
        hb_flush = HandBuilder(flush)
        self.assertEqual(HandBuilder.FLUSH, hb_flush.score_hand(), "didn't find flush")

        hb_s_flush = HandBuilder(self.cards2) # 10-high flush
        high_card = Card(10, C.CLUBS)
        self.assertEqual(HandBuilder.STRAIGHT_FLUSH + high_card.score_value(), hb_s_flush.score_hand(), "didn't find straight flush")

    def test_score_hand_straight(self):
        """Tests finding a straight"""
        high_card = Card(C.JACK, C.SPADES)
        straight = self.cards1 + [high_card] # Jack-high straight
        hb = HandBuilder(straight)
        self.assertEqual((HandBuilder.STRAIGHT + high_card.score_value()), hb.score_hand(), "didn't score the straight")

    def test_score_hand_high(self):
        """Score a hand with only a high card"""
        high_card = Card(C.ACE, C.CLUBS)
        aceHigh = [Card(2, C.DIAMONDS), Card(4, C.SPADES), Card(C.JACK, C.CLUBS),
                   Card(7, C.HEARTS), high_card]
        hb = HandBuilder(aceHigh)
        self.assertEqual(HandBuilder.HIGH_CARD + high_card.score_value(), hb.score_hand(), "didn't score an ace high")

    def test_score_hand_pair(self):
        """Scores a hand with a pair"""
        pairAces = [Card(2, C.DIAMONDS), Card(4, C.SPADES), Card(C.JACK, C.CLUBS),
                   Card(C.ACE, C.HEARTS), Card(C.ACE, C.CLUBS)]
        hb = HandBuilder(pairAces)
        self.assertEqual(HandBuilder.PAIR, hb.score_hand(), "didn't find a pair")

    def test_score_hand_two_pair(self):
        """Finds two pairs"""
        twoPair = [Card(2, C.DIAMONDS), Card(2, C.SPADES), Card(C.JACK, C.CLUBS),
                   Card(C.ACE, C.HEARTS), Card(C.ACE, C.CLUBS)]
        hb = HandBuilder(twoPair)
        self.assertEqual(HandBuilder.TWO_PAIR, hb.score_hand(), "didn't find two pair")

    def test_score_hand_trips(self):
        """Finds 3 of a kinds"""
        trips = [Card(2, C.DIAMONDS), Card(C.ACE, C.SPADES), Card(C.JACK, C.CLUBS),
                 Card(C.ACE, C.HEARTS), Card(C.ACE, C.CLUBS)]
        hb = HandBuilder(trips)
        self.assertEqual(HandBuilder.TRIPS, hb.score_hand(), "didn't find trips")

    def test_score_hand_full_house(self):
        """Finds a full house"""
        full_house = [Card(2, C.DIAMONDS), Card(C.ACE, C.SPADES),
                      Card(2, C.CLUBS), Card(C.ACE, C.HEARTS),
                      Card(C.ACE, C.CLUBS)]
        hb = HandBuilder(full_house)
        self.assertEqual(HandBuilder.FULL_HOUSE, hb.score_hand(), "didn't find full house")

    def test_score_hand_quads(self):
        """Finds 4 of a kind"""
        quads = [Card(C.ACE, C.DIAMONDS), Card(C.ACE, C.SPADES),
                 Card(2, C.CLUBS), Card(C.ACE, C.HEARTS),
                 Card(C.ACE, C.CLUBS)]
        hb = HandBuilder(quads)
        self.assertEqual(HandBuilder.QUADS, hb.score_hand(), "didn't find quads")

class HandFinderTest(unittest.TestCase):
    """Tests edge cases of the find_hand function"""

    def test_easy_find_hand(self):
        """Tests the 5-card case (no-op)"""
        full_house = [Card(2, C.DIAMONDS), Card(C.ACE, C.SPADES),
                      Card(2, C.CLUBS), Card(C.ACE, C.HEARTS),
                      Card(C.ACE, C.CLUBS)]
        hb = HandBuilder(full_house)
        best_hand = hb.find_hand()

        self.assertEqual(len(full_house), len(best_hand), "hands not the same length")
        for card in best_hand:
            self.assertTrue(card in full_house, "card missing from best hand")

    def test_6_card_hand(self):
        """Tests a simple version of the 6-card case"""
        full_house = [Card(2, C.DIAMONDS), Card(C.ACE, C.SPADES),
                      Card(2, C.CLUBS), Card(C.ACE, C.HEARTS),
                      Card(C.ACE, C.CLUBS), Card(4, C.DIAMONDS)]
        answer = full_house[:len(full_house) - 1]
        hb = HandBuilder(full_house)
        best_hand = hb.find_hand()

        self.assertTrue(len(answer), len(best_hand))
        for card in best_hand:
            self.assertTrue(card in answer)

    def test_7_card_hand(self):
        """Tests a 7-card case"""
        two_pair = [Card(2, C.DIAMONDS), Card(2, C.SPADES),
                    Card(5, C.HEARTS), Card(5, C.SPADES),
                    Card(C.ACE, C.HEARTS), Card(C.ACE, C.DIAMONDS)]
        # Don't care which 2 gets picked
        partial_answer = [Card(5, C.HEARTS), Card(5, C.SPADES),
                          Card(C.ACE, C.HEARTS), Card(C.ACE, C.DIAMONDS)]

        hb = HandBuilder(two_pair)
        best_hand = hb.find_hand()

        self.assertEqual(len(best_hand), len(partial_answer) + 1)
        for card in partial_answer:
            self.assertTrue(card in best_hand, "card missing from the answer")

if __name__ == '__main__':
    unittest.main()
