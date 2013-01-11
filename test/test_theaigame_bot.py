import sys
import unittest
from pokeher.theaigame_bot import TheAiGameBot

class TheAiGameBotTest(unittest.TestCase):
    """Tests instantiating the bot and feeding it a couple lines"""
    def test_both_instantiation(self):
        # TODO: use Mock and actually test stderr and stdout
        bot = TheAiGameBot(sys.stdout, sys.stderr)
        self.assertTrue(bot)
