
class Blinds(object):
    """Players must post a blind to buy in"""
    def __init__(self, small_blind, big_blind):
        assert big_blind > small_blind
        self.small_blind = small_blind
        self.big_blind = big_blind

        self.hands_per_level = 10
        self.hands_this_level = 0

    def hand_blinds(self):
        """Prints out the blinds for TheAiGame bots"""
        return ["Match smallBlind {sb}".format(sb=self.small_blind),
                "Match bigBlind {bb}".format(bb=self.big_blind),]

    def check_raise_blinds(self):
        pass # TODO

    def match_blinds(self):
        return ['Settings handsPerLevel {hpl}'.format(hpl=self.hands_per_level)]

class NoBetLimit(object):
    """Players can bet any amount, at any time"""

    def check_bet(self, pot, bet):
        """Returns true if the bet is legal given the current pot"""
        return bet > 0
