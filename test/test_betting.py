import unittest
from arena.betting import *


class NoBetLimitTest(unittest.TestCase):
    def test_bets(self):
        """Makes sure all positive bets are allowed in no limit"""
        limit = NoBetLimit()
        pot = 100
        self.assertTrue(limit.check_bet(pot, 30))
        self.assertTrue(limit.check_bet(pot, 100*pot))
        self.assertFalse(limit.check_bet(pot, -30))


class BlindsTest(unittest.TestCase):
    def test_preconditions(self):
        """Checks the blinds constructor"""
        try:
            Blinds(20, 10)
        except AssertionError:
            pass
        else:
            self.fail("allowed big blind to be smaller")

    def test_blinds_printer(self):
        """Tests that the blinds are printed correctly"""
        blinds = Blinds(10, 20)
        hand_print = set(blinds.hand_blinds())
        self.assertTrue("Match small_blind 10" in hand_print)
        self.assertTrue("Match big_blind 20" in hand_print)


class BlindManagerTest(unittest.TestCase):
    def setUp(self):
        self.bots = ['a', 'b', 'c', 'd', 'e']
        self.bm = BlindManager(5, self.bots)

    def test_match_blinds(self):
        match_blinds = self.bm.match_blinds()
        self.assertEqual(match_blinds, ['Settings handsPerLevel 5'])

    def test_start_blinds(self):
        """Checks the initial blinds conditions"""
        bm = self.bm
        _, sb = bm.next_sb()
        self.assertEqual(sb, 'a')
        _, bb = bm.next_bb()
        self.assertEqual(bb, 'b')

    def test_blinds_advance(self):
        """Check that after one hand the blinds advance"""
        bm = self.bm
        bm.finish_hand()
        _, sb = bm.next_sb()
        self.assertEqual(sb, 'b')
        _, bb = bm.next_bb()
        self.assertEqual(bb, 'c')

    def test_blinds_after_elimination(self):
        """Check that blinds advance after a player is eliminated"""
        bm = self.bm
        bm.finish_hand()
        bm.finish_hand()
        bm.eliminate_player('c')
        _, sb = bm.next_sb()
        self.assertEqual(sb, 'd')
        _, bb = bm.next_bb()
        self.assertEqual(bb, 'e')


class BettingRoundTest(unittest.TestCase):
    def setUp(self):
        self.bots = ['a', 'b', 'c']
        self.bets = {'a': 10, 'b': 20}
        self.br = BettingRound(self.bots, self.bets)

    def test_say_pot(self):
        br = self.br
        pots = br.say_pot()
        self.assertIn('Match max_win_pot 30', pots)
        self.assertIn('Match amount_to_call 10', br.say_to_call('a'))
        self.assertIn('Match amount_to_call 0', br.say_to_call('b'))

    def test_constructor(self):
        """Check state after constructing a new BettingRound"""
        br = BettingRound(self.bots, self.bets)
        self.assertEqual(br.pot, 30)
        self.assertEqual(br.sidepot, 20)
        self.assertEqual(br.high_better, None)  # no high better after blinds
        self.assertEqual(br.bets['c'], 0)
        self.assertEqual(br.bots, self.bots)

    def test_bet_staked(self):
        """Checks the state methods"""
        br = self.br
        self.assertTrue(br.can_bet('c'))  # 0 bet so far
        self.assertTrue(br.can_bet('a'))  # small blind
        self.assertTrue(br.can_bet('b'))  # BB
        self.assertFalse(br.can_bet('d'))  # bogus

        for name in self.bots:
            self.assertTrue(br.is_staked(name))

    def test_next_bettor(self):
        """Checks the next bettor"""
        self.assertEqual(self.br.next_better(), 'c')

    def test_fold_next_bettor(self):
        """Checks that after a fold we find the next bettor"""
        br = self.br
        self.assertEqual(br.next_better(), 'c')
        br.post_bet('c', 0)  # C folds
        self.assertEqual(br.next_better(), 'a')

    def test_round_over(self):
        """Tests that after a C fold, B check and A call the round ends"""
        br = self.br
        self.assertFalse(br.post_fold('c'))
        self.assertFalse(br.check_bet_size('a', 9)) # too small
        self.assertTrue(br.check_bet_size('a', 50)) # big enough
        self.assertTrue(br.post_bet('a', 10))
        self.assertTrue(br.post_bet('b', 0))
        self.assertEqual(br.next_better(), None)
        remaining = br.remaining_players()
        self.assertEqual(len(remaining), 2)
        self.assertTrue('a' in remaining)
        self.assertTrue('b' in remaining)

    def test_heads_up_fold(self):
        br = self.br
        self.assertFalse(br.post_fold('c'))
        self.assertFalse(br.post_fold('a'))
        # A & C fold, so B (BB) wins
        self.assertEqual(br.pot, 30)
        self.assertEqual(br.next_better(), None)
        self.assertEqual(br.remaining_players(), ['b'])

    def test_post_bet(self):
        """Checks posting a new bet"""
        br = self.br
        success = br.post_bet('c', 100)

        self.assertTrue(success)
        self.assertEqual(br.sidepot, 100)
        self.assertEqual(br.pot, 130)
        self.assertEqual(br.high_better, 'c')

        for bot in self.bots:
            self.assertTrue(br.is_staked(bot))

    def test_heads_up_blinds(self):
        bots = ['a', 'b']
        bets = {'a': 10, 'b': 20}
        br = BettingRound(bots, bets)
        self.assertTrue(br.post_bet('a', 10))
        self.assertTrue(br.post_bet('b', 0))
        self.assertEqual(br.big_blind, 'b')
        # Betting round should be over after 'b' checks
        self.assertEqual(br.next_better(), None)

    def test_heads_up_bb_bets(self):
        bots = ['a', 'b']
        bets = {'a': 10, 'b': 20}
        br = BettingRound(bots, bets)
        self.assertTrue(br.post_bet('a', 10))
        self.assertTrue(br.post_bet('b', 10))
        self.assertEqual(br.big_blind, 'b')
        self.assertEqual(br.next_better(), 'a')
        self.assertEqual(br.pot, 50)
        self.assertEqual(br.sidepot, 30)

    def test_checks_around(self):
        bots = ['a', 'b']
        bets = {}
        br = BettingRound(bots, bets)
        self.assertTrue(br.post_bet('a', 0))
        self.assertTrue(br.post_bet('b', 0))
        self.assertEqual(br.next_better(), None)

    def test_fold(self):
        """Tests that betting 0 causes a fold"""
        br = self.br
        success = br.post_bet('c', 0)

        self.assertFalse(success)
        self.assertEqual(br.pot, 30)
        self.assertFalse(br.is_staked('c'))
        self.assertFalse(br.can_bet('c'))
