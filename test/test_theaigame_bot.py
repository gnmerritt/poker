import sys
import unittest
from pokeher.theaigame_bot import TheAiGameBot

class TheAiGameBotTest(unittest.TestCase):
    def test_bot_instantiation(self):
        """Tests instantiating the bot"""
        # TODO: use Mock and actually test stderr and stdout
        bot = TheAiGameBot(sys.stdout, sys.stderr)
        self.assertTrue(bot)
