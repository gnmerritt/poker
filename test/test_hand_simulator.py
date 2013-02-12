import unittest
from pokeher.hand_simulator import HandSimulator
import pokeher.constants as C
from pokeher.cards import Card, Hand

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
        """Checks that adding table cards works, and that 4ok always wins"""
        hand = Hand(Card(10, C.SPADES), Card(3, C.SPADES))
        table_cards = [Card(3, C.CLUBS),
                       Card(3, C.HEARTS),
                       Card(3, C.DIAMONDS)]
        simulator = HandSimulator(hand, table_cards)

        self.assertEqual(len(simulator.deck), 47)

        win_percentage = simulator.simulate(5)
        self.assertEqual(win_percentage, 100)
