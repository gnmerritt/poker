import unittest

from arena.gauntlet import GauntletArena


class GauntletTest(unittest.TestCase):
    # TODO: probably should test the actual game runner...

    def test_initial(self):
        gauntlet = GauntletArena("foo")
        self.assertEqual(gauntlet.wins, {})
        self.assertEqual(gauntlet.tries, {})
        self.assertEqual(gauntlet.challenger, "foo")
        string = repr(gauntlet)
        self.assertEquals("Challenger: foo", string)

    def test_after_win(self):
        gauntlet = GauntletArena("foo")
        gauntlet.handle_winners("baddie", ["foo"])
        self.assertEqual(gauntlet.wins, {"baddie": 1})

        gauntlet.handle_winners("baddie", ["foo"])
        self.assertEqual(gauntlet.wins, {"baddie": 2})
        gauntlet.tries = {"baddie": 2}
        string = repr(gauntlet)
        self.assertIn("PASS", string)
        self.assertIn("2/2 (100.0%)", string)

    def test_after_loss(self):
        gauntlet = GauntletArena("foo")
        gauntlet.handle_winners("baddie", ["baddie"])
        self.assertEqual(gauntlet.wins, {"baddie": 0})
