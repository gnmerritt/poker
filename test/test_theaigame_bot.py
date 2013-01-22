import unittest
from pokeher.theaigame_bot import TheAiGameBot

class TheAiGameBotTest(unittest.TestCase):
    """Test that the bot class is instantiated properly and has all the methods
    that it's supposed to"""
    def setUp(self):
        self.bot = TheAiGameBot(None, None, None)

    def test_bot_instantiation(self):
        """Tests instantiating the bot"""
        self.assertTrue(self.bot)

    def test_bot_methods(self):
        """Tests that the bot has all the I/O methods"""
        self.assertTrue(self.bot.run)
        self.assertTrue(self.bot.say)
        self.assertTrue(self.bot.log)

    def test_mixed_in_methods(self):
        """Tests that the bot has all the parser & action methods"""
        self.assertTrue(self.bot.set_up_parser)
        self.assertTrue(self.bot.bet)
        self.assertTrue(self.bot.fold)
        self.assertTrue(self.bot.call)
        self.assertTrue(self.bot.check)
