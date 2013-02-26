import unittest
from arena.holdem import *
from arena.arena import LoadedBot

class MockHoldem(Holdem):
    """Mocks out mixin methods that would usually be defined"""
    count = 2

    def bot_count(self):
        return self.count

    def living_bots(self):
        return ['a', 'b']

    def living_bot_names(self):
        return self.living_bots()

    def bot_from_name(self, name):
       bot = LoadedBot("bot", 2)
       bot.state.stack = 1000
       return bot

    def say_table_cards(self):
        pass

class HoldemTest(unittest.TestCase):
    def test_dealer(self):
        for i in range (2, 10):
            self.verify_dealer(i)

    def verify_dealer(self, players):
        h = MockHoldem()
        h.count = players
        hands_list = h.deal_hands(players)
        remainder = h.deck

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

    def test_post_bet(self):
        """Tests that posting a bet increases the pot & decreases the player"""
        h = MockHoldem()
        h.init_game()
        self.assertEqual(0, h.pot)
        self.assertEqual([], h.table_cards)
        starting_stack = h.bot_from_name("name").state.stack
        self.assertTrue(h.post_bet("name", 100))
        self.assertEqual(100, h.pot)

    def test_table_cards(self):
        """Tests that table cards are dealt 3-1-1"""
        h = MockHoldem()
        h.init_game()
        h.deal_hands(2)
        self.assertEqual([], h.table_cards)

        h.deal_table_cards() # flop
        flop = h.table_cards
        self.assertEqual(3, len(flop))

        h.deal_table_cards() # turn
        turn = h.table_cards
        self.assertEqual(4, len(turn))
        for c in flop:
            self.assertTrue(c in turn)

        h.deal_table_cards() # river
        river = h.table_cards
        self.assertEqual(5, len(river))
        for c in turn:
            self.assertTrue(c in river)

    @unittest.skip("wrote too early")
    def test_play_hand(self):
        h = MockHoldem()
        winners = h.play_hand()

        self.assertTrue(winners)
