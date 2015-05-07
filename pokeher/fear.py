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
        self.data = data_obj

    def minimum_handscore(self):
        # TODO: this is extremely simple right now...
        table_value = self.find_table_score(self.data.table_cards)
        if self.bet > 0 and table_value.type <= C.TRIPS:
            table_value.type += 1
        return handscore.HandScore(table_value.type)

    def find_table_score(self, cards):
        builder = handscore.HandBuilder(cards)
        return builder.score_hand()
