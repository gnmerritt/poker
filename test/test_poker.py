import unittest
import pokeher.cards as cards
import pokeher.constants as C
from arena.poker import *
from arena_mocks import ScriptedArena

class BettingRoundTest(unittest.TestCase):
    """"Tests that PokerHand can adjucate a full betting round"""
    def build_run_hand(self, actions):
        bots = [a[0] for a in actions]
        arena = ScriptedArena(actions)
        hand = PokerHand(arena, bots)
        return hand.betting_round(bots)

    def test_raise_call(self):
        """Tests that a betting round ends after rase & call"""
        actions = [
            ['bot_0', 'raise 20'],
            ['bot_1', 'call 20'],
        ]
        ended, remaining = self.build_run_hand(actions)
        self.assertFalse(ended, "hand shouldnt have ended")
        self.assertEqual(len(remaining), 2)

    def test_raise_fold(self):
        actions = [
            ['bot_0', 'check 0'],
            ['bot_1', 'raise 10'],
            ['bot_0', 'fold'],
        ]
        ended, remaining = self.build_run_hand(actions)
        self.assertTrue(ended)
        self.assertEqual(len(remaining), 1)

class ShowdownTest(unittest.TestCase):
    def test_winner(self):
        bot_hands = {
            'aces': [cards.Card(C.ACE, C.HEARTS), cards.Card(C.ACE, C.SPADES)],
            'junk': [cards.Card(6, 3), cards.Card(5, 2)],
        }
        table = [cards.Card(4, 1), cards.Card(C.KING, 2), cards.Card(3, 2),
                 cards.Card(C.QUEEN, 0), cards.Card(9, 0)]
        showdown = Showdown(bot_hands, table)
        winners = showdown.winners
        self.assertEqual(winners, ['aces'])

    def test_split_pot(self):
        bot_hands = {
            'qj1': [cards.Card(C.QUEEN, C.HEARTS), cards.Card(C.JACK, C.SPADES)],
            'qj2': [cards.Card(C.QUEEN, C.CLUBS), cards.Card(C.JACK, C.HEARTS)],
        }
        table = [cards.Card(4, 1), cards.Card(C.KING, 2), cards.Card(3, 2),
                 cards.Card(C.QUEEN, 0), cards.Card(9, 0)]
        showdown = Showdown(bot_hands, table)
        winners = showdown.winners
        self.assertTrue('qj1' in winners)
        self.assertTrue('qj2' in winners)
        self.assertEqual(len(winners), 2)
