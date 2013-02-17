import unittest
from arena.arena import *

class BotStateTest(unittest.TestCase):
    def test_constructor(self):
        bs = BotState(1)
        self.assertEqual(bs.name, "bot_1")
        self.assertEqual(bs.seat, 1)
        self.assertEqual(bs.stack, 0)
        self.assertEqual(bs.stake, 0)

class PyArenaTest(unittest.TestCase):
    def test_arena_methods(self):
        """Make sure the arena can do everything it needs to"""
        arena = PyArena()
        self.assertTrue(arena.run)
        self.assertTrue(arena.load_bot)
        self.assertTrue(arena.bot_count)
        self.assertTrue(arena.play_match)

    def test_load_bots(self):
        """See if we can load a bot"""
        arena = PyArena()
        arena.load_bot("pokeher/theaigame_bot.py")
        self.assertEqual(arena.bot_count(), 1)

    def test_load_bad_filename(self):
        """Don't want load_bot exploding on us"""
        arena = PyArena()
        arena.load_bot("asdlfj23u90dj")
        self.assertTrue(arena)
        self.assertEqual(arena.bot_count(), 0)
