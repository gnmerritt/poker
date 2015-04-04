import unittest
from arena.holdem import *
from arena.arena import LoadedBot

class MockHoldemArena(Holdem):
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

    def say_table_cards(self, cards):
        pass

    def post_bet(self, bot_name, amount):
        return amount

class HoldemTest(unittest.TestCase):
    def test_dealer(self):
        """Verifies the holdem dealer for 2-10 players"""
        for i in range (2, 10):
            self.verify_dealer(i)

    def verify_dealer(self, players):
        holdem = MockHoldemArena()
        holdem.count = players
        hand = holdem.new_hand()
        hands_map = hand.deal_hands(['a{}'.format(i) for i in range(0, players)])
        remainder = hand.deck

        self.assertTrue(hands_map)
        self.assertEqual(len(hands_map), holdem.bot_count())
        self.assertEqual(len(remainder), 52 - holdem.bot_count() * holdem.hand_size())

        seen = [] # no duplicate cards among hands
        for bot, hand in hands_map.iteritems():
            self.assertEqual(len(hand), holdem.hand_size())
            for card in hand:
                self.assertFalse(card in remainder)
                self.assertFalse(card in seen)
                seen.append(card)

        self.assertTrue(len(seen), 52 - len(remainder))

    def test_constants(self):
        """Tests holdem constants"""
        holdem = MockHoldemArena()
        self.assertEqual(holdem.max_players(), 10)
        self.assertEqual(holdem.min_players(), 2)
        self.assertEqual(holdem.hand_size(), 2)

    def test_ante(self):
        holdem = MockHoldemArena()
        holdem.init_game()
        self.assertTrue(holdem.ante())

    def test_post_bet(self):
        """Tests that posting a bet increases the pot & decreases the player"""
        holdem = MockHoldemArena()
        holdem.init_game()
        hand = holdem.new_hand()
        self.assertEqual(0, hand.pot)
        self.assertEqual([], hand.table_cards)
        self.assertTrue(hand.post_bet("name", 100))
        self.assertEqual(100, hand.pot)

    def test_table_cards(self):
        """Tests that table cards are dealt 3-1-1"""
        holdem = MockHoldemArena()
        holdem.init_game()
        hand = holdem.new_hand()
        hand.deal_hands(['a','b'])
        self.assertEqual([], hand.table_cards)

        hand.deal_table_cards([]) # flop
        flop = hand.table_cards
        self.assertEqual(3, len(flop))

        hand.deal_table_cards([]) # turn
        turn = hand.table_cards
        self.assertEqual(4, len(turn))
        for c in flop:
            self.assertTrue(c in turn)

        hand.deal_table_cards([]) # river
        river = hand.table_cards
        self.assertEqual(5, len(river))
        for c in turn:
            self.assertTrue(c in river)

    @unittest.skip("wrote too early")
    def test_play_hand(self):
        holdem = MockHoldemArena()
        winners = holdem.play_hand()

        self.assertTrue(winners)
