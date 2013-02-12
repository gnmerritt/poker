import unittest
from pokeher.cards import *
import pokeher.constants as C
from pokeher.handscore import *

class HandScoreTest(unittest.TestCase):
    def test_handscore_ordering(self):
        """Tests the total ordering on HandScore"""
        a = HandScore()
        a.type = HandScore.HIGH_CARD

        b = HandScore()
        b.type = HandScore.HIGH_CARD
        self.assertTrue(a == b, "scores not equal")

        b.kicker = C.ACE
        a.kicker = C.JACK
        self.assertTrue(a < b, "kicker doesn't work")

        b.type = HandScore.FLUSH
        self.assertTrue(b > a, "flush didn't beat J-high")

class HandBuilderTest(unittest.TestCase):
    cards1 = [Card(7, C.CLUBS),
              Card(8, C.CLUBS),
              Card(9, C.CLUBS),
              Card(10, C.CLUBS) ]
    cards2 = cards1 + [Card(6, C.CLUBS)]
    cards3 = cards1 + [Card(6, C.SPADES), Card(2, C.DIAMONDS), Card(C.ACE, C.HEARTS)]
    cards4 = cards1 + [Card(3, C.CLUBS)]

    def test_flush_finder_empty(self):
        """Tests that select_flush_suit degrades gracefully"""
        hb = HandBuilder([])
        self.assertEqual(-1, hb.select_flush_suit())

        hb = HandBuilder(None)
        self.assertEqual(-1, hb.select_flush_suit())

    def test_flush_finder(self):
        """Tests the flush finder"""
        hb = HandBuilder(self.cards1)
        self.assertFalse(hb.select_flush_suit())

        hb2 = HandBuilder(self.cards2)
        self.assertEqual(C.CLUBS, hb2.select_flush_suit())

        hb3 = HandBuilder(self.cards3)
        self.assertEqual(-1, hb3.select_flush_suit())

        hb4 = HandBuilder(self.cards4)
        self.assertEqual(C.CLUBS, hb4.select_flush_suit())

    def test_score_hand_empty(self):
        """Tests that the HB doesn't explode for bad entries"""
        hb = HandBuilder([])
        self.assertEqual(HandScore(), hb.score_hand())

        hb2 = HandBuilder(None)
        self.assertEqual(HandScore(), hb2.score_hand())

    def test_score_hand_flush(self):
        """Tests finding flushes and straight flushes"""
        high_card = Card(C.ACE, C.CLUBS)
        flush = self.cards1 + [high_card]
        hb_flush = HandBuilder(flush)
        self.assertEqual(HandScore.FLUSH, hb_flush.score_hand().type, "didn't find flush")

        hb_s_flush = HandBuilder(self.cards2) # 10-high flush
        high_card = Card(10, C.CLUBS)
        score = hb_s_flush.score_hand()
        self.assertEqual(HandScore.STRAIGHT_FLUSH, score.type, "didn't find straight flush")
        self.assertEqual((10, 9, 8, 7, 6), score.kicker, "didn't get the kicker right")

    def test_score_hand_straight(self):
        """Tests finding a straight"""
        high_card = Card(C.JACK, C.SPADES)
        straight = self.cards1 + [high_card] # Jack-high straight
        hb = HandBuilder(straight)
        score = hb.score_hand()
        self.assertEqual(HandScore.STRAIGHT, score.type, "didn't score the straight")
        self.assertEqual((11, 10, 9, 8, 7), score.kicker)

    def test_score_hand_high(self):
        """Score a hand with only a high card"""
        high_card = Card(C.ACE, C.CLUBS)
        aceHigh = [Card(2, C.DIAMONDS), Card(4, C.SPADES), Card(C.JACK, C.CLUBS),
                   Card(7, C.HEARTS), high_card]
        score = HandBuilder(aceHigh).score_hand()
        self.assertEqual(HandScore.HIGH_CARD, score.type, "didn't score an ace high")
        self.assertEqual((14,11,7,4,2), score.kicker)

    def test_score_hand_pair(self):
        """Scores a hand with a pair"""
        pairAces = [Card(2, C.DIAMONDS), Card(4, C.SPADES), Card(C.JACK, C.CLUBS),
                   Card(C.ACE, C.HEARTS), Card(C.ACE, C.CLUBS)]
        score = HandBuilder(pairAces).score_hand()
        self.assertEqual(HandScore.PAIR, score.type)
        self.assertEqual((14,14,11,4,2), score.kicker)

    def test_score_hand_two_pair(self):
        """Finds two pairs"""
        twoPair = [Card(2, C.DIAMONDS), Card(2, C.SPADES), Card(C.JACK, C.CLUBS),
                   Card(C.ACE, C.HEARTS), Card(C.ACE, C.CLUBS)]
        hb = HandBuilder(twoPair)
        score = hb.score_hand()
        self.assertEqual(HandScore.TWO_PAIR, score.type, "didn't find two pair")

        # check the kicker to make sure the pairs got sorted
        self.assertEqual((14,14,2,2,11), score.kicker)

    def test_score_hand_trips(self):
        """Finds 3 of a kind"""
        trips = [Card(2, C.DIAMONDS), Card(C.ACE, C.SPADES), Card(C.JACK, C.CLUBS),
                 Card(C.ACE, C.HEARTS), Card(C.ACE, C.CLUBS)]
        hb = HandBuilder(trips)
        self.assertEqual(HandScore.TRIPS, hb.score_hand().type, "didn't find trips")

    def test_score_hand_full_house(self):
        """Finds a full house"""
        full_house = [Card(2, C.DIAMONDS), Card(C.ACE, C.SPADES),
                      Card(2, C.CLUBS), Card(C.ACE, C.HEARTS),
                      Card(C.ACE, C.CLUBS)]
        score = HandBuilder(full_house).score_hand()
        self.assertEqual(HandScore.FULL_HOUSE, score.type, "didn't find full house")
        self.assertEqual((14,14,14,2,2), score.kicker)

    def test_score_hand_quads(self):
        """Finds 4 of a kind"""
        quads = [Card(2, C.DIAMONDS), Card(2, C.SPADES),
                 Card(3, C.CLUBS), Card(2, C.HEARTS),
                 Card(2, C.CLUBS)]
        score = HandBuilder(quads).score_hand()
        self.assertEqual(HandScore.QUADS, score.type, "didn't find quads")
        self.assertEqual((2,2,2,2,3), score.kicker)

    def test_preflop_edge_cases(self):
        """Tests cases that seemed to be weird in the preflop job"""
#A-Spades, K-Spades, 9-Spades, 8-Spades, 2-Spades)
        hand = [Card(C.ACE, C.SPADES), Card(C.KING, C.SPADES), Card(9, C.SPADES),
                Card(8, C.SPADES), Card(2, C.SPADES)]
        score = HandBuilder(hand).score_hand()
        self.assertEqual(HandScore.FLUSH, score.type)
        self.assertEqual((14, 13, 9, 8, 2), score.kicker)

class HandFinderTest(unittest.TestCase):
    """Tests edge cases of the find_hand function"""

    def test_easy_find_hand(self):
        """Tests the 5-card case (no-op)"""
        full_house = [Card(2, C.DIAMONDS), Card(C.ACE, C.SPADES),
                      Card(2, C.CLUBS), Card(C.ACE, C.HEARTS),
                      Card(C.ACE, C.CLUBS)]
        hb = HandBuilder(full_house)
        best_hand, _ = hb.find_hand()

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
        best_hand, score = hb.find_hand()

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
        best_hand, score = hb.find_hand()

        self.assertEqual(len(best_hand), len(partial_answer) + 1)
        for card in partial_answer:
            self.assertTrue(card in best_hand, "card missing from the answer")

if __name__ == '__main__':
    unittest.main()
