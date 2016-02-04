import unittest
import tempfile
import os
import shutil

from arena.local_arena import LocalIOArena
from arena.hand_log import HandLog
from pokeher.actions import GameAction


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
            stacks = arena.bot_stacks()
            self.assertEqual(stacks['bot_0'], 1000)
            self.assertEqual(stacks.keys(), ['bot_0'])

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

    def test_hand_log_writing(self):
        arena = LocalIOArena()
        arena.key = "fake-uuid-woo-boom"
        temp = tempfile.mkdtemp()
        arena.output_directory = temp
        arena.current_round = 0

        log = HandLog({})
        log.unix_epoch_s = lambda: 10
        log.action("bot_1", GameAction(GameAction.FOLD))
        arena.write_hand_log(log)

        written_file = os.path.join(temp, arena.key, "hand_0.json")
        written_handle = open(written_file, 'r')
        contents = written_handle.read()
        self.assertEquals(contents, '{"initial_stacks": {}, "actions": [{"player": "bot_1", "data": 0, "event": "Fold", "ts": 10}]}')

        shutil.rmtree(temp)
