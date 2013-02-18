import unittest
from arena.betting import Blinds, NoBetLimit, BettingRound

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
        try:
            blinds = Blinds(20, 10)
        except AssertionError:
            pass
        else:
            self.fail("allowed big blind to be smaller")

    def test_blinds_printer(self):
        """Tests that the blinds are printed correctly"""
        blinds = Blinds(10, 20)
        hand_print = set(blinds.hand_blinds())
        self.assertTrue("Match smallBlind 10" in hand_print)
        self.assertTrue("Match bigBlind 20" in hand_print)

class BettingRoundTest(unittest.TestCase):
    def setUp(self):
        self.bots = ['a', 'b', 'c']
        self.bets = {'a' : 10, 'b' : 20}
        self.br = BettingRound(self.bots, self.bets)

    def test_constructor(self):
        """Check state after constructing a new BettingRound"""
        br = self.br
        self.assertEqual(br.pot, 30)
        self.assertEqual(br.sidepot, 20)
        self.assertEqual(br.high_better, None) # no high better after blinds
        self.assertEqual(br.bets['c'], 0)
        self.assertEqual(br.bots, self.bots)

    def test_bet_staked(self):
        """Checks the state methods"""
        br = self.br
        self.assertTrue(br.can_bet('c')) # 0 bet so far
        self.assertTrue(br.can_bet('a')) # small blind
        self.assertTrue(br.can_bet('b')) # BB
        self.assertFalse(br.can_bet('d')) # bogus

        for name in self.bots:
            self.assertTrue(br.is_staked(name))

    def test_next_bettor(self):
        """Checks the next bettor"""
        self.assertEqual(self.br.next_better(), 'c')

    def test_fold_next_bettor(self):
        """Checks that after a fold we find the next bettor"""
        br = self.br
        self.assertEqual(br.next_better(), 'c')
        br.post_bet('c', 0) # C folds
        self.assertEqual(br.next_better(), 'a')

    def test_round_over(self):
        """Tests that after a C fold, B check and A call the round ends"""
        br = self.br
        self.assertFalse(br.post_bet('c', 0))
        self.assertTrue(br.post_bet('a', 10))
        self.assertTrue(br.post_bet('b', 0))
        self.assertEqual(br.next_better(), None)

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

    def test_fold(self):
        """Tests that betting 0 causes a fold"""
        br = self.br
        success = br.post_bet('c', 0)

        self.assertFalse(success)
        self.assertEqual(br.pot, 30)
        self.assertFalse(br.is_staked('c'))
        self.assertFalse(br.can_bet('c'))
