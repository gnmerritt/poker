import unittest

from pokeher.actions import GameAction


class ActionTest(unittest.TestCase):
    def test_actions_eq(self):
        call = GameAction(GameAction.CALL)
        self.assertTrue(call.is_call())
        self.assertEqual("Call", call.name())

        check = GameAction(GameAction.CHECK)
        self.assertTrue(check.is_check())
        self.assertEquals("<GameAction type=C, amount=0>", repr(check))
        self.assertNotEqual(call, check)

    def test_raises_eq(self):
        r1 = GameAction(GameAction.RAISE, 10)
        r2 = GameAction(GameAction.RAISE, 30)
        self.assertNotEqual(r1, r2)
        self.assertTrue(r1.is_raise())
        self.assertEquals("Raise", r1.name())
        self.assertEquals("<GameAction type=R, amount=10>", repr(r1))
