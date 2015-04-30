import cython_random as random
from utility import MathUtils as mu


class BetTier(object):
    """A bet tier object that identifiers the size of a bet"""
    def __init__(self, parent, name, test_func):
        self.parent = parent
        self.name = name
        self.test_func = test_func

    def test(self, bet):
        self.parent.bet = bet
        return self.test_func(self.parent)


class BetTiers(object):
    """Bet tiers in ascending order of what we assume from seeing the bet"""
    def __init__(self, pot, big_blind, is_preflop=False, opponent_stack=None):
        self.pot = pot
        self.bb = big_blind
        self.stack = opponent_stack
        self.bet = None

        def bet_percent(values):
            return mu.percentage(values.bet, values.pot)

        # TODO: different for preflop
        self.tiers = [
            BetTier(self, "CHECK", lambda v: v.bet == 0),
            BetTier(self, "MIN_RAISE", lambda v: v.bet == v.bb or bet_percent(v) <= 12),
            BetTier(self, "RAISE", lambda v: bet_percent(v) <= 80),
            BetTier(self, "BIG_RAISE", lambda v: bet_percent(v) <= 130),
            BetTier(self, "OVERBET", lambda v: True)
        ]

    def tier(self, bet):
        all_in = BetTier(self, "ALL_IN", lambda v: True)
        if self.stack == bet:
            return all_in

        for tier in self.tiers:
            if tier.test(bet):
                return tier


class BetSizeCalculator(object):
    """Mixin class that provides bet sizing calculations to the brain"""
    def to_call(self, silent=False):
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
        return self.data.stacks[self.data.me]

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
        return self.__round_bet(bet_raise)

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
        return self.__round_bet(bet)

    def __round_bet(self, val):
        if val is not None:
            return int(round(val))
