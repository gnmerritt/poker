import unittest
import twisted.trial.unittest as trial_unit
from twisted.internet import defer

from arena.net_arena import TwistedNLHEArena


class DummyProtocol(object):
    def __init__(self):
        self.lines = []

    def sendLine(self, line):
        self.lines.append(line)


class NetArenaTests(unittest.TestCase):
    def setUp(self):
        self.arena = TwistedNLHEArena()
        self.protocol = DummyProtocol()
        self.arena.add_bot("ABC_KEY", self.protocol, name="Nibbler")

    def test_load_bot(self):
        bot_key = self.arena.bot_from_name("ABC_KEY")
        self.assertFalse(bot_key)
        bot = self.arena.bot_from_name("bot_0")
        self.assertTrue(bot)
        self.assertEqual(bot.state.source, "ABC_KEY")
        self.assertEqual(self.arena.bot_keys.get("ABC_KEY"), "bot_0")

    def test_get_action(self):
        def callback(action):
            self.assertFalse(callback.fired, "callback fired twice")
            self.assertEqual(action, self.arena.get_parsed_action("fold"))
            callback.fired = True
        callback.fired = False
        d = defer.Deferred()
        d.addCallback(callback)

        self.arena.bot_keys['bot_0'] = "bot_0"
        self.arena.get_action("bot_0", d)
        self.assertEqual(self.arena.waiting_on, "bot_0")
        self.assertEqual(self.arena.action_deferred, d)
        self.assertIn("Action bot_0 7000", self.protocol.lines)

        self.arena.bot_said("bot_1", "Something we ignored")
        self.assertFalse(callback.fired)

        self.arena.bot_said("bot_0", "fold")
        self.assertTrue(callback.fired)

    def test_time_for_move(self):
        delay = self.arena.get_time_for_move("foasdfsof")
        self.assertEqual(delay, self.arena.TIME_PER_MOVE)

        nibbler_delay = self.arena.get_time_for_move("bot_0")
        self.assertEqual(nibbler_delay, 7)

    def test_bot_timed_out(self):
        abc = self.arena.bot_from_name("bot_0")
        self.assertEqual(abc.state.timeouts, 0, "no timeouts initially")
        self.assertEqual(abc.state.timebank, 5, "full initial timebank")

        self.arena.bot_timed_out("bot_0")

        abc = self.arena.bot_from_name("bot_0")
        self.assertEqual(abc.state.timeouts, 1, "timeout added")
        self.assertEqual(abc.state.timebank, 0, "timebank exhausted")


class NetArenaGameTest(trial_unit.TestCase):
    def setUp(self):
        self.arena = TwistedNLHEArena()
        self.b1_protocol = DummyProtocol()
        self.arena.add_bot("ABC_KEY", self.b1_protocol, name="B1")

    def test_game_starts(self):
        """Game should begin after a second bot joins"""
        b2_protocol = DummyProtocol()
        self.arena.add_bot("DEF_KEY", b2_protocol)
        lines = b2_protocol.lines
        self.assertIn("bot_0 seat 0", lines)
        self.assertIn("Settings your_bot bot_1", lines)
        self.assertIn("bot_0 post 10", lines)

        self.arena.on_bot_timeout.cancel()  # placate twistd tests
