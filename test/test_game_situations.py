import unittest

from twisted.internet import defer

from arena.local_arena import LocalIOArena


class GameExampleTests(unittest.TestCase):
    """Tests of situations encountered in games that broke the bot"""
    AIG_BOT = "pokeher/theaigame_bot.py"

    def __run_test(self, actions):
        with LocalIOArena(silent=True) as arena:
            arena.print_bot_output = False
            arena.load_bot(self.AIG_BOT)
            self.assertEqual(arena.bot_count(), 1)
            for a in actions:
                arena.tell_bots([a])
            def callback(action):
                self.assertTrue(action)
            d = defer.Deferred()
            d.addCallback(callback)
            arena.get_action("bot_0", d)

    def test_timeout_after_flop(self):
        """Something goes bump in the night. This also explodes if extra logging gets added"""
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
        self.__run_test(actions)

    def test_main_loop_exception(self):
        """Seeing 'main loop exception' errors during test games"""
        actions = [
            "Settings your_bot bot_0",
            "Settings timebank 10000",
            "Settings time_per_move 500",
            "Match round 15",
            "Match small_blind 15",
            "Match big_blind 30",
            "Match on_button player2",
            "bot_0 stack 2290",
            "player2 stack 1710",
            "player2 post 15",
            "bot_0 post 30",
            "bot_0 hand [Ts,3h]",
            "player2 raise 60",
            "Match max_win_pot 120",
            "Match amount_to_call 60",
        ]
        self.__run_test(actions)
