import unittest
from pokeher.theaigame_bot import TheAiGameBot

class TheAiGameBotTest(unittest.TestCase):
    def test_bot_instantiation(self):
        """Tests instantiating the bot"""
        # TODO: use Mock and actually test stderr and stdout
        bot = TheAiGameBot(None, None)
        self.assertTrue(bot)

    def test_bot_methods(self):
        bot = TheAiGameBot(None, None)
        self.assertTrue(bot.run)
        self.assertTrue(bot.say)
        self.assertTrue(bot.log)

    def test_mixed_in_methods(self):
        bot = TheAiGameBot(None, None)
        self.assertTrue(bot.set_up_parser)
        self.assertTrue(bot.bet)
        self.assertTrue(bot.fold)
        self.assertTrue(bot.call)
        self.assertTrue(bot.check)
