import unittest
from arena.arena import PyArena


class SpyingArena(PyArena):
    pass


class GameExampleTests(unittest.TestCase):
    """Tests of situations encountered in games that broke the bot"""
    AIG_BOT = "pokeher/theaigame_bot.py"

    def test_timeout_after_flop(self):
        """Something goes bump in the night"""
        actions = [
            "Settings your_bot bot_0",
            "Settings timebank 10000",
            "Settings time_per_move 500",
            "Match round 1",
            "Match small_blind 10",
            "Match big_blind 20",
            "Match on_button player2",
            "bot_0 stack 2000",
            "player2 stack 2000",
            "player2 post 10",
            "bot_0 post 20",
            "bot_0 hand [Td,Ac]",
            "player2 call 10",
            "Match max_win_pot 40",
            "Match amount_to_call 0",
            "bot_0 raise 28",
            "player2 call 28",
            "Match table [9d,6d,5h]",
            "Match max_win_pot 96",
            "Match amount_to_call 0",
        ]
        with SpyingArena(silent=True) as arena:
            arena.print_bot_output = False
            arena.load_bot(self.AIG_BOT)
            self.assertEqual(arena.bot_count(), 1)
            for a in actions:
                arena.tell_bots([a])
            action = arena.get_action("bot_0")
            self.assertTrue(action)
