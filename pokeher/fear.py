from bet_sizing import BetTiers
import handscore
import constants as C


class Fear(object):
    """Mix-in object for managing fear in the Brain"""
    def update_fear(self, bet):
        if not self.data.table_cards:
            # TODO: should include re-raises eventually
            preflop_fear = OpponentPreflopFear(self.data, bet)
            self.data.preflop_fear = max(self.data.preflop_fear,
                                         preflop_fear.hand_filter())
        else:
            hand_fear = OpponentHandRangeFear(self.data, bet)
            self.data.hand_fear = max(self.data.hand_fear,
                                      hand_fear.minimum_handscore())


class OpponentPreflopFear(object):
    """Class that tracks opponent's preflop actions to estimate their
    starting hand strength"""
    RAISE_FEARS = {
        "CHECK": -1,
        "MIN_RAISE": 40,
        "RAISE": 45,
        "BIG_RAISE": 50,
        "OVERBET": 60,
    }

    def __init__(self, data_obj, to_call):
        pot = data_obj.pot
        bb = data_obj.big_blind
        is_preflop = not data_obj.table_cards
        # TODO: opponent stack?
        tiers = BetTiers(pot, bb, is_preflop)
        self.tier = tiers.tier(to_call)

    def hand_filter(self):
        return self.RAISE_FEARS.get(self.tier.name, -1)


class OpponentHandRangeFear(object):
    """Class that looks at opponent's bets to estimate their minimum hand"""
    def __init__(self, data_obj, bet):
        self.bet = bet

    def minimum_handscore(self):
        # TODO: this is extremely simple right now...
        # it should probably actually reflect the cards showing on the table
        minimum = C.PAIR if self.bet > 0 else C.HIGH_CARD
        return handscore.HandScore(minimum)
