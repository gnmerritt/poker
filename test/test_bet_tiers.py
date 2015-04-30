import unittest
import random

from pokeher.bet_sizing import BetTiers


class BetTierTest(unittest.TestCase):
    """Tests that we put bets in the correct tiers"""
    def setUp(self):
        self.tiers = BetTiers(pot=500, big_blind=20, is_preflop=False)

    def test_random_bets(self):
        """Verifies that random bets all get bucketed to a tier"""
        for _ in range(25):
            bet = random.randint(20, 1200)
            tier = self.tiers.tier(bet)
            self.assertTrue(tier)

    def test_bet_sizes(self):
        """Verifies that different bet sizes are classified correctly"""
        def tier_name_for(bet):
            return self.tiers.tier(bet).name

        self.assertEqual(tier_name_for(0), "CHECK")
        self.assertEqual(tier_name_for(20), "MIN_RAISE")
        self.assertEqual(tier_name_for(200), "RAISE")
        self.assertEqual(tier_name_for(500), "BIG_RAISE")
        self.assertEqual(tier_name_for(750), "OVERBET")

    def test_all_ins(self):
        tiers = BetTiers(pot=500, big_blind=20, opponent_stack=300)
        self.assertEqual(tiers.tier(300).name, "ALL_IN")
