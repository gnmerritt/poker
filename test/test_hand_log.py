import unittest
import tempfile

from arena.hand_log import HandLog
from pokeher.theaigame import CardBuilder
from pokeher.actions import GameAction


def c(card):
    return CardBuilder().from_2char(card)


class HandLogTest(unittest.TestCase):
    def fake_ts(self, ts):
        return lambda: ts

    def setUp(self):
        self.log = HandLog({})
        self.log.unix_epoch_s = self.fake_ts(10)

    def test_empty_initially(self):
        stacks = {'a': 10}
        log = HandLog(stacks)
        self.assertEqual([], log.actions)
        self.assertEqual(stacks, log.initial_stacks)

    def test_hands(self):
        hands = {
            'a': [c('2h'), c('Ad')],
            'b': [c('3c'), c('Ks')]
        }
        self.log.hands(hands)
        self.assertEqual(2, len(self.log.actions))
        hand = {
            "player": "a", "ts": 10, "event": "CARDS",
            "data": ['2h', 'Ad']
        }
        self.assertIn(hand, self.log.actions)
        hand['player'] = "b"
        hand['data'] = ['3c', 'Ks']
        self.assertIn(hand, self.log.actions)

    def test_bet(self):
        self.log.action("bot_1", GameAction(GameAction.RAISE, 10))
        the_raise = {
            "player": "bot_1", "ts": 10, "event": "Raise",
            "data": 10
        }
        self.assertEqual([the_raise], self.log.actions)

    def test_pot(self):
        self.log.pot(310)
        pot = {
            "player": "TABLE", "ts": 10, "event": "POT", "data": 310
        }
        self.assertEqual([pot], self.log.actions)

    def test_remaining(self):
        players = ['bot_0', 'bot_1']
        self.log.remaining(players)
        remaining = {
            "player": "TABLE", "ts": 10, "event": "REMAINING", "data": players
        }
        self.assertEqual([remaining], self.log.actions)

    def test_write(self):
        self.log.action("bot_1", GameAction(GameAction.FOLD))
        output = tempfile.SpooledTemporaryFile()
        self.log.to_file(output)
        output.seek(0)
        written = output.read()
        self.assertEqual(written, '{"initial_stacks": {}, "actions": [{"player": "bot_1", "data": 0, "event": "Fold", "ts": 10}]}')
