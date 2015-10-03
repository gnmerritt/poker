import unittest

from agents.call_bot import CallBot
from agents.check_fold_bot import CheckFoldBot
from agents.raise_bot import RaiseBot
from agents.call_raise_bot import CallRaiseBot


class CallBotTest(unittest.TestCase):
    def setUp(self):
        self.bot = CallBot([], [], [])
        self.bot.add_brain()
        self.bot.call = self.call
        self.called = False

    def call(self, amount):
        self.called = True

    def test_call_bot(self):
        self.bot.brain.do_turn("bot", 100)
        self.assertTrue(self.called)


class CheckFoldBotTest(unittest.TestCase):
    def setUp(self):
        self.bot = CheckFoldBot([], [], [])
        self.bot.add_brain()
        self.bot.check = self.check
        self.checked = False

    def check(self):
        self.checked = True

    def test_check_fold_bot(self):
        self.bot.brain.do_turn("bot", 100)
        self.assertTrue(self.checked)


class RaiseBotTest(unittest.TestCase):
    def setUp(self):
        self.bot = RaiseBot([], [], [])
        self.bot.add_brain()
        self.bot.bet = self.bet
        self.raised = 0

    def bet(self, amount):
        self.raised = amount

    def test_raise_bot(self):
        self.bot.brain.do_turn("bot", 100)
        self.assertGreater(self.raised, 0)


class CallRaiseBotTest(unittest.TestCase):
    def setUp(self):
        self.bot = CallRaiseBot([], [], [])
        self.bot.add_brain()
        self.bot.bet = self.bet
        self.bot.call = self.call
        self.raises = 0
        self.calls = 0

    def bet(self, amount):
        self.raises += 1

    def call(self, amount):
        self.calls += 1

    def test_call_raise_bot(self):
        for _ in range(50):
            self.bot.brain.do_turn("bot", 100)
        self.assertGreater(self.raises, 10)
        self.assertGreater(self.calls, 10)
