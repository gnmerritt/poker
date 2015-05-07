import unittest
from pokeher.hand_simulator import HandSimulator
from pokeher.handscore import HandScore
import pokeher.constants as C
from pokeher.cards import Card, Hand
import pokeher.preflop_equity


class HandSimulatorTest(unittest.TestCase):
    """Makes sure that the hand simulator is functioning correctly"""

    def test_constructor(self):
        """Sanity checks on the HandSimulator initial state"""
        hand = Hand(Card(10, C.SPADES), Card(4, C.DIAMONDS))
        simulator = HandSimulator(hand)

        self.assertFalse(simulator.table_cards)
        self.assertEqual(len(simulator.deck), 50)
        self.assertFalse(Card(10, C.SPADES) in simulator.deck)
        self.assertFalse(Card(4, C.DIAMONDS) in simulator.deck)

        win_percentage = simulator.simulate(10)
        self.assertTrue(isinstance(win_percentage, float))
        self.assertTrue(win_percentage > 0)

    def test_constructor_with_table(self):
        """Checks that adding table cards works, and that quads always win"""
        hand = Hand(Card(10, C.SPADES), Card(3, C.SPADES))
        table_cards = [Card(3, C.CLUBS),
                       Card(3, C.HEARTS),
                       Card(3, C.DIAMONDS)]
        simulator = HandSimulator(hand, table_cards)

        self.assertEqual(len(simulator.deck), 47)

        win_percentage = simulator.simulate(5)
        self.assertEqual(win_percentage, 100)

    def test_hand_filter(self):
        equity = pokeher.preflop_equity.PreflopEquity()
        hand = Hand(Card(10, C.SPADES), Card(3, C.SPADES))
        simulator = HandSimulator(hand, [], preflop_equity=equity.data)

        ace = Card(C.ACE, C.HEARTS)
        ace2 = Card(C.ACE, C.SPADES)
        king = Card(C.KING, C.SPADES)
        three = Card(3, C.HEARTS)
        two = Card(2, C.SPADES)

        # aces win 84% of the time preflop
        self.assertTrue(simulator.passes_filter(ace, ace2, 30))
        self.assertFalse(simulator.passes_filter(ace, ace2, 95))
        self.assertTrue(simulator.passes_filter(ace, king, 65))
        self.assertTrue(simulator.passes_filter(king, three, 30))
        self.assertFalse(simulator.passes_filter(three, two, 40))

    def test_min_hand(self):
        """Verifies that the minimum score filter works"""
        ace = Card(C.ACE, C.HEARTS)
        king = Card(C.KING, C.SPADES)
        three = Card(3, C.HEARTS)
        two = Card(2, C.SPADES)
        seven = Card(7, C.HEARTS)

        cards = [ace, king, three, two]
        hand = Hand(king, seven)
        simulator = HandSimulator(hand, cards)

        # KK should win pretty often
        self.assertGreater(simulator.simulate(100), 50)

        min_hand = HandScore(C.TRIPS)
        # but not against other trips
        self.assertLess(simulator.simulate(100, min_hand=min_hand), 5)
