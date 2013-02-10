import unittest
from arena.theaigame_arena import TheAiGameArena

class TheAiGameArenaTest(unittest.TestCase):
    def test_instantiation(self):
        """Make sure we can instantiate an TheAiGameArena"""
        arena = TheAiGameArena()
        self.assertTrue(arena)
