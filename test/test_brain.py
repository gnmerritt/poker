import unittest
from pokeher.wiring import BufferPokerBot
from pokeher.theaigame import TheAiGameParserDelegate, TheAiGameActionDelegate
from pokeher.brain import Brain
from pokeher.cards import Card, Hand
from pokeher.cards import Constants as C

class BrainTestBot(BufferPokerBot, TheAiGameParserDelegate, TheAiGameActionDelegate):
    pass

class BrainTest(unittest.TestCase):
    def setUp(self):
        self.fake_in = []
        self.fake_out = []
        self.fake_log = []

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


if __name__ == '__main__':
    unittest.main()
