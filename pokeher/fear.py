from bet_sizing import BetTiers


class OpponentHandFear(object):
    """Class that tracks opponent's actions to estimate their hand strength"""
    RAISE_FEARS = {
        "CHECK": -1,
        "MIN_RAISE": 30,
        "RAISE": 35,
        "BIG_RAISE": 45,
        "OVERBET": 55,
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
