from __future__ import division

import cython_random as random
from utility import MathUtils as mu


class BetTier(object):
    """A bet tier object that identifiers the size of a bet"""
    def __init__(self, name, test_func):
        self.name = name
        self.test_func = test_func

    def test(self, data):
        return self.test_func(data)


class BetTiers(object):
    """Bet tiers in ascending order of what we assume from seeing the bet"""
    def __init__(self, pot, big_blind, is_preflop=False, opponent_stack=None):
        self.pot = pot
        self.bb = big_blind
        self.stack = opponent_stack
        self.bet = None

        self.tiers = self.prefop_tiers() if is_preflop else self.post_flop_tiers()

    def prefop_tiers(self):
        def num_blinds(values):
            return values.bet / values.bb

        return [
            BetTier("CHECK", lambda v: v.bet < v.bb),
            BetTier("MIN_RAISE", lambda v: v.bet == v.bb),
            BetTier("RAISE", lambda v: num_blinds(v) < 3),
            BetTier("BIG_RAISE", lambda v: num_blinds(v) < 6),
            BetTier("OVERBET", lambda v: True)
        ]


    def post_flop_tiers(self):
        def bet_percent(values):
            return mu.percentage(values.bet, values.pot)

        return [
            BetTier("CHECK", lambda v: v.bet == 0),
            BetTier("MIN_RAISE", lambda v: v.bet == v.bb or bet_percent(v) <= 12),
            BetTier("RAISE", lambda v: bet_percent(v) <= 80),
            BetTier("BIG_RAISE", lambda v: bet_percent(v) <= 130),
            BetTier("OVERBET", lambda v: True)
        ]

    def tier(self, bet):
        """Returns the tier that matches this bet"""
        all_in = BetTier("ALL_IN", lambda v: True)
        if self.stack == bet:
            return all_in

        self.bet = bet
        for tier in self.tiers:
            if tier.test(self):
                return tier


class BetSizeCalculator(object):
    """Mixin class that provides bet sizing calculations to the brain"""
    def to_call(self, silent=True):
        to_call = self.data.to_call
        if not silent:
            self.bot.log("bot={}, pot={}, to call={}" \
                         .format(self.data.me, self.data.pot, to_call))
        return to_call

    def pot_odds(self):
        """Return the pot odds, or how much we need to gain to call"""
        to_call = self.to_call()
        return mu.percentage(to_call, self.data.pot + to_call)

    def our_stack(self):
        """Returns our current stack size"""
        return self.data.stacks.get(self.data.me, 0)

    def big_raise(self, source=None):
        """Returns a big raise:
           preflop: 3-5 BB
           after flop: 80-150% of the pot
        """
        pot = self.data.pot
        if not self.data.table_cards:
            bb = self.data.big_blind
            bet_raise = random.uniform(3, 5) * bb
        else:
            bet_raise = random.uniform(0.8, 1.5) * pot
        self.bot.log(" big raise of {r} (pot={p}) from {s}"
                     .format(r=bet_raise, p=pot, s=source))
        return self.finalize_bet(bet_raise)

    def minimum_bet(self, source=None):
        """Returns a minimum bet:
           preflop: 1-3 * BB
           after flop: 1/6 - 2/5 of the pot
        """
        if not self.data.table_cards:
            bb = self.data.big_blind
            bet = random.uniform(1, 3) * bb
        else:
            pot = self.data.pot
            bet = random.uniform(0.16, 0.4) * pot
        self.bot.log(" small raise of {b} from {s}"
                     .format(b=bet, s=source))
        return self.finalize_bet(bet)

    def finalize_bet(self, val):
        stack = self.our_stack()
        remaining = stack - val
        if remaining > 0 and mu.percentage(remaining, stack) < 25:
            self.bot.log(" increased bet by {} to all-in".format(remaining))
            val = stack
        return int(round(val))
