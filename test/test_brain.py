import unittest
from pokeher.wiring import BufferPokerBot
from pokeher.theaigame import TheAiGameParserDelegate, TheAiGameActionDelegate
from pokeher.brain import Brain
from pokeher.cards import Card, Hand
from pokeher.timer import Timer
import pokeher.constants as C

class BrainTestBot(BufferPokerBot, TheAiGameParserDelegate, TheAiGameActionDelegate):
    def add_brain(self):
        self.brain = Brain(self)

    def log(self, msg):
        pass

class BrainTest(unittest.TestCase):
    def setUp(self):
        self.fake_in = []
        self.fake_out = []
        self.fake_log = []
        self.data = MockData()
        self.data.to_call = 20
        self.data.pot = 140
        self.data.hand = Hand(Card(C.ACE, C.DIAMONDS), Card(C.ACE, C.HEARTS))
        self.data.table_cards = []
        self.data.time_per_move = 500
        self.data.me = 'bot_0'
        self.data.bets = {}

    def test_got_output(self):
        """Tests that the bot does something when it hits the turn marker"""
        self.fake_in = ['Settings your_bot bot_0',
                        'bot_0 hand [Ac,As]',
                        'Action bot_0 5000']
        bot = BrainTestBot(self.fake_in, self.fake_out, self.fake_log)
        bot.run()

        self.assertEqual(bot.brain.data.me, 'bot_0')
        self.assertTrue(bot.brain.data.hand)
        self.assertTrue(self.fake_out)

    def test_preflop_equity_loaded(self):
        """Tests that the preflop equity data loaded correctly"""
        bot = BrainTestBot(self.fake_in, self.fake_out, self.fake_log)
        self.assertTrue(bot.brain.preflop_equity)
        self.assertEqual(len(bot.brain.preflop_equity.keys()), 169)

    def test_preflop_sanity(self):
        """Pull some stuff from the preflop equity and spot check it"""
        bot = BrainTestBot(self.fake_in, self.fake_out, self.fake_log)
        bad_hand = Hand(Card(2, C.CLUBS), Card(3, C.DIAMONDS))
        sample_key = bad_hand.simple()

        self.assertTrue(sample_key in bot.brain.preflop_equity.keys())
        bad_equity = bot.brain.preflop_equity[sample_key]
        self.assertTrue(bad_equity > 0.2)

        good_hand = Hand(Card(C.ACE, C.SPADES), Card(C.ACE, C.DIAMONDS))
        good_equity = bot.brain.preflop_equity[good_hand.simple()]
        self.assertTrue(good_equity > bad_equity)

class TestBrainBets(unittest.TestCase):
    """Checks the predefined bets"""
    def setUp(self):
        bot = MockBot()
        self.brain = Brain(bot)
        d = MockData()
        d.big_blind = 20
        d.pot = 130
        self.brain.data = d

    def verify_bet(self, bet, bottom, top):
        self.assertTrue(bet >= bottom)
        self.assertTrue(bet <= top)

    def test_big_raise(self):
        """Tests the big bet range"""
        bet = self.brain.big_raise()
        pot = self.brain.data.pot
        self.verify_bet(bet, pot * 0.7, pot * 1.5)

    def test_minimum_bet(self):
        """Tests the minimum bet range"""
        bb = self.brain.data.big_blind
        bet = self.brain.minimum_bet()
        self.verify_bet(bet, bb * 2, bb * 4)

class BettingFunctionalTests(BrainTest):
    """End-to-end tests with cards and everything"""
    def test_preflop_betting(self):
        """Sanity test of the preflop betting"""
        bot = MockBot()
        brain = Brain(bot)
        brain.data = self.data

        # 20 to call, 140 in the pot
        self.assertAlmostEqual(brain.pot_odds(), 100 * 2.0/(14 + 2))
        brain.do_turn('bot_0', 1000)
        self.assertTrue(bot.raise_amount > 0) # shouldn't fold with a pair of aces

    def test_river_betting(self):
        """Sanity tests of betting with common cards"""
        self.data.table_cards = [Card(C.ACE, C.SPADES),
                                 Card(2, C.DIAMONDS),
                                 Card(7, C.SPADES)]
        bot = MockBot()
        brain = Brain(bot)
        brain.data = self.data
        brain.iterations = 100 # smaller for unit tests
        brain.do_turn('bot_0', 500)
        self.assertTrue(bot.raise_amount > 0)

    def test_timing_out(self):
        """Tests that the brain simulator doesn't run forever"""
        self.data.table_cards = [Card(C.ACE, C.SPADES),
                                 Card(2, C.DIAMONDS),
                                 Card(7, C.SPADES)]
        bot = MockBot()
        brain = Brain(bot)
        brain.data = self.data
        brain.iterations = 10000 # will time out
        with Timer() as t:
            brain.do_turn('bot_0', 250)
            self.assertTrue(bot.raise_amount > 0)
        self.assertTrue(t.secs < 0.250)

    def test_time_per_move(self):
        """Tests that the brain uses time_per_move over the max time"""
        self.data.table_cards = [Card(C.ACE, C.SPADES),
                                 Card(2, C.DIAMONDS),
                                 Card(7, C.SPADES)]
        bot = MockBot()
        brain = Brain(bot)
        brain.data = self.data
        brain.data.time_per_move = 250
        brain.iterations = 10000 # will time out
        with Timer() as t:
            brain.do_turn('bot_0', 10000)
            self.assertTrue(bot.raise_amount > 0)
        self.assertTrue(t.secs < 0.250)

class MockBot(object):
    """For testing the brain by itself"""
    def __init__(self):
        self.bet_amount = 0

    def set_up_parser(self, a, b):
        return None

    def call(self, amount):
        self.bet_amount = amount

    def bet(self, amount):
        self.raise_amount = amount

    def log(self, msg):
        print msg

class MockData(object):
    pass

if __name__ == '__main__':
    unittest.main()
