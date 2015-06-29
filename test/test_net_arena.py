import unittest
import twisted.trial.unittest as trial_unit

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


    def test_get_action(self):
        def callback(action):
            self.assertFalse(callback.fired, "callback fired twice")
            self.assertEqual(action, self.arena.get_parsed_action("fold"))
            callback.fired = True
        callback.fired = False

        self.arena.get_action("bot_0", callback)
        self.assertEqual(self.arena.waiting_on, "bot_0")
        self.assertEqual(self.arena.action_callback, callback)
        self.assertIn("Action bot_0 1000", self.protocol.lines)

        self.arena.bot_said("bot_1", "Something we ignored")
        self.assertFalse(callback.fired)

        self.arena.bot_said("bot_0", "fold")
        self.assertTrue(callback.fired)


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
