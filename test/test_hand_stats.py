import unittest

from arena.hand_stats import HandStats


class HandStatTest(unittest.TestCase):
    def test_stats(self):
        stats = HandStats()
        stats.tick(50, 0)
        stats.tick(100, 4)
        stats.tick(75, 2)

        representation = str(stats)
        self.assertTrue(representation)
        self.assertIn("avg_pot=75.00", representation)
        self.assertIn("Preflop=(33.33%)", representation)
        self.assertIn("Flop=(33.33%)", representation)
        self.assertIn("Turn=(33.33%)", representation)
