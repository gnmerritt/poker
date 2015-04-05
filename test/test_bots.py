import unittest
from arena.bots import *


class BotStateTest(unittest.TestCase):
    def test_constructor(self):
        """Checks initial bot state"""
        bs = BotState(1)
        self.assertEqual(bs.name, "bot_1")
        self.assertEqual(bs.seat, 1)
        self.assertEqual(bs.stack, bs.INITIAL_CHIPS)
        self.assertEqual(bs.stake, 0)


class LoadedBotTest(unittest.TestCase):
    def test_tell_bot(self):
        """Make sure that piping info to a bot works"""
        pass # TODO

    def test_lifecycle(self):
        """Checks name, seat, is_active and kill for loaded bots"""
        bot = LoadedBot("", 0)

        self.assertEqual('bot_0', bot.state.name)
        self.assertEqual(0, bot.state.seat)
        self.assertTrue(bot.is_active)

        bot.kill()
        self.assertFalse(bot.is_active)
