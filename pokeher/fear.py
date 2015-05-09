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


class OpponentFear(object):
    def __init__(self, data_obj, to_call):
        pot = data_obj.pot
        bb = data_obj.big_blind
        is_preflop = not data_obj.table_cards
        self.data = data_obj
        self.bet = to_call
        # TODO: opponent stack?
        tiers = BetTiers(pot, bb, is_preflop)
        self.tier = tiers.tier(to_call)


class OpponentPreflopFear(OpponentFear):
    """Class that tracks opponent's preflop actions to estimate their
    starting hand strength"""
    RAISE_FEARS = {
        "CHECK": -1,
        "MIN_RAISE": 40,
        "RAISE": 45,
        "BIG_RAISE": 50,
        "OVERBET": 60,
    }

    def hand_filter(self):
        return self.RAISE_FEARS.get(self.tier.name, -1)


class OpponentHandRangeFear(OpponentFear):
    """Class that looks at opponent's bets to estimate their minimum hand"""
    RAISE_FEARS = {
        "CHECK": (0, None),
        "MIN_RAISE": (0, C.QUEEN),
        "RAISE": (1, None),
        "BIG_RAISE": (1, C.QUEEN),
        "OVERBET": (2, None),
    }

    def minimum_handscore(self):
        table_best = self.find_table_score(self.data.table_cards)
        type_increase, kicker = self.RAISE_FEARS[self.tier.name]
        table_best.type += type_increase
        fear_kicker = tuple([kicker] * 5)
        table_best.kicker = max(table_best.kicker, fear_kicker)
        return table_best

    def find_table_score(self, cards):
        builder = handscore.HandBuilder(cards)
        score = builder.score_hand()
        score.type = max(score.type, 0)
        return score
