import unittest
from arena.local_arena import LocalIOArena


class PyArenaTest(unittest.TestCase):
    def test_arena_methods(self):
        """Make sure the arena can do everything it needs to"""
        arena = LocalIOArena()
        self.assertTrue(arena.run)
        self.assertTrue(arena.load_bot)
        self.assertTrue(arena.bot_count)
        self.assertTrue(arena.play_match)

    def test_load_bots(self):
        """See if we can load a bot"""
        with LocalIOArena() as arena:
            arena.load_bot("pokeher/theaigame_bot.py")
            self.assertEqual(arena.bot_count(), 1)

    def test_load_bad_filename(self):
        """Don't want load_bot exploding on us"""
        arena = LocalIOArena()
        arena.load_bot("asdlfj23u90dj")
        self.assertTrue(arena)
        self.assertEqual(arena.bot_count(), 0)

    def test_pot_splitting(self):
        arena = LocalIOArena()
        winnings = arena.split_pot(pot=16, num_winners=2)
        self.assertEqual(len(winnings), 2)
        for prize in winnings:
            self.assertEqual(prize, 8)

    def test_uneven_pot_splitting(self):
        arena = LocalIOArena()
        winnings = arena.split_pot(pot=15, num_winners=2)
        self.assertEqual(len(winnings), 2)
        self.assertIn(7, winnings)
        self.assertIn(8, winnings)
