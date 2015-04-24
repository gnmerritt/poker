import unittest
import pokeher.cards as cards
import pokeher.constants as C
from arena.poker import *
from arena_mocks import ScriptedArena

class BettingRoundTest(unittest.TestCase):
    """"Tests that PokerHand can adjucate a full betting round"""
    def build_run_hand(self, actions, all_ins=[]):
        bots = [a[0] for a in actions]
        arena = ScriptedArena(actions)
        for bot, bet in all_ins:
            arena.all_ins[bot] = bet
        hand = PokerHand(arena, bots)
        return hand, hand.betting_round(bots)

    def test_raise_call(self):
        """Tests that a betting round ends after rase & call"""
        actions = [
            ['bot_0', 'raise 20'],
            ['bot_1', 'call 20'],
        ]
        _, (ended, remaining) = self.build_run_hand(actions)
        self.assertFalse(ended, "hand shouldnt have ended")
        self.assertEqual(len(remaining), 2)

    def test_raise_fold(self):
        actions = [
            ['bot_0', 'check 0'],
            ['bot_1', 'raise 10'],
            ['bot_0', 'fold'],
        ]
        _, (ended, remaining) = self.build_run_hand(actions)
        self.assertTrue(ended)
        self.assertEqual(len(remaining), 1)

    def test_all_in_call(self):
        actions = [
            ['bot_0', 'raise 10'],
            ['bot_1', 'raise 100'], # pot now 120
            ['bot_0', 'call 100'], # bot_0 all in, only posts 10 (pot down to 40)
        ]
        hand, (ended, remaining) = self.build_run_hand(actions, [['bot_0',10]])
        self.assertFalse(ended, "all in shouldn't end the hand")
        self.assertEqual(hand.pot, 130, "all in added wrong")
        # TODO: this is wrong, pot should be 40 - refund big raise the
        # difference that bot_0 couldn't call

    def test_min_raise(self):
        actions = [
            ['bot_0', 'raise 10'], # pot 10
            ["bot_1", "raise 20"], # pot 30
            # smaller than minimum raise, gets bumped to raise 20
            ["bot_0", "raise 1"],  # call 20 + raise 20, pot = 80
        ]
        hand, (ended, remaining) = self.build_run_hand(actions)
        self.assertEqual(hand.pot, 80)
        self.assertFalse(ended)

    def test_min_reraise(self):
        actions = [
            ["bot_0", "raise 50"], # pot 50
            ["bot_1", "raise 60"], # pot 160
            ["bot_0", "raise 50"], # c60, raise 60, pot = 280
        ]
        hand, (ended, remaining) = self.build_run_hand(actions)
        self.assertEqual(hand.pot, 280)
        self.assertFalse(ended)
        self.assertIn('bot_0', remaining)
        self.assertIn('bot_1', remaining)


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
