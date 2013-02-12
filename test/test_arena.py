import unittest
from arena.arena import PyArena

class PyArenaTest(unittest.TestCase):
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
