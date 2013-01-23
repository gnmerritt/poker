import unittest
from pokeher.wiring import BufferPokerBot
from pokeher.theaigame import TheAiGameParserDelegate, TheAiGameActionDelegate
from pokeher.brain import Brain

class BrainTestBot(BufferPokerBot, TheAiGameParserDelegate, TheAiGameActionDelegate):
    pass

class BrainTest(unittest.TestCase):
    def setUp(self):
        self.fake_in = []
        self.fake_out = []
        self.fake_log = []
        self.bot = BrainTestBot(self.fake_in, self.fake_out, self.fake_log)

    def test_got_output(self):
        """Tests that the bot does something when it hits the turn marker"""
        self.fake_in.append('go 5000')
        self.bot.run()
        self.assertTrue(self.fake_out)

    def test_preflop_equity_loaded(self):
        """Tests that the preflop equity data loaded correctly"""
        self.assertTrue(self.bot.brain.preflop_equity)
        self.assertEqual(len(self.bot.brain.preflop_equity.keys()), 1326)

if __name__ == '__main__':
    unittest.main()
