import unittest

from arena.net_arena import TwistedNLHEArena


class DummyProtocol(object):
    def sendLine(self, line):
        pass


class NetArenaTests(unittest.TestCase):
    def setUp(self):
        self.arena = TwistedNLHEArena()
        self.arena.add_bot("ABC_KEY", DummyProtocol(), name="Nibbler")

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

        self.arena.bot_said("bot_1", "Something we ignored")
        self.assertFalse(callback.fired)

        self.arena.bot_said("bot_0", "fold")
        self.assertTrue(callback.fired)
