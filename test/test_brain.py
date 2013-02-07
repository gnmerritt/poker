import unittest
from pokeher.wiring import BufferPokerBot
from pokeher.theaigame import TheAiGameParserDelegate, TheAiGameActionDelegate
from pokeher.brain import Brain
from pokeher.cards import Card, Hand
from pokeher.cards import Constants as C

class BrainTestBot(BufferPokerBot, TheAiGameParserDelegate, TheAiGameActionDelegate):
    def log(self, msg):
        pass

class BrainTest(unittest.TestCase):
    def setUp(self):
        self.fake_in = []
        self.fake_out = []
        self.fake_log = []
        self.data = MockData()
        self.data.sidepot = 20 # to call
        self.data.pot = 140
        self.data.hand = Hand(Card(C.ACE, C.DIAMONDS), Card(C.ACE, C.HEARTS))
        self.data.table_cards = []

    def test_got_output(self):
        """Tests that the bot does something when it hits the turn marker"""
        self.fake_in = ['Settings yourBot bot_0',
                        'bot_0 hand [Ac,As]',
                        'go 5000']
        bot = BrainTestBot(self.fake_in, self.fake_out, self.fake_log)
        bot.run()

        self.assertEqual(bot.brain.data.me, 'bot_0')
        self.assertTrue(bot.brain.data.hand)
        self.assertTrue(self.fake_out)

    def test_preflop_equity_loaded(self):
        """Tests that the preflop equity data loaded correctly"""
        bot = BrainTestBot(self.fake_in, self.fake_out, self.fake_log)
        self.assertTrue(bot.brain.preflop_equity)
        self.assertEqual(len(bot.brain.preflop_equity.keys()), 1326)

    def test_preflop_sanity(self):
        """Pull some stuff from the preflop equity and spot check it"""
        bot = BrainTestBot(self.fake_in, self.fake_out, self.fake_log)
        bad_hand = Hand(Card(2, C.CLUBS), Card(3, C.DIAMONDS))
        sample_key = repr(bad_hand)

        self.assertTrue(sample_key in bot.brain.preflop_equity.keys())
        bad_equity = bot.brain.preflop_equity[sample_key]
        self.assertTrue(bad_equity > 0.2)

        good_hand = Hand(Card(C.ACE, C.SPADES), Card(C.ACE, C.DIAMONDS))
        good_equity = bot.brain.preflop_equity[repr(good_hand)]
        self.assertTrue(good_equity > bad_equity)

    def test_preflop_betting(self):
        """Sanity test of the preflop betting"""
        data = self.data
        bot = MockBot()
        brain = Brain(bot)
        brain.data = data

        self.assertEqual(brain.pot_odds(), 12.5) # 20 to call, 140 in the pot

        brain.do_turn(1000)
        self.assertTrue(bot.bet_amount > 0) # shouldn't fold with a pair of aces

class MockBot(object):
    """For testing the brain by itself"""
    def __init__(self):
        self.bet_amount = 0

    def set_up_parser(self, a, b):
        return None

    def call(self, amount):
        self.bet_amount = amount

    def log(self, msg):
        print msg

class MockData(object):
    pass

if __name__ == '__main__':
    unittest.main()
