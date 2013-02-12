
class Blinds(object):
    """Players must post a blind to buy in"""
    def __init__(self, small_blind, big_blind):
        assert big_blind > small_blind
        self.small_blind = small_blind
        self.big_blind = big_blind

    def print_for_theaigames(self, output):
        """Prints out the blinds for TheAiGame bots"""
        output.write("Match smallBlind {sb}\n".format(sb=self.small_blind))
        output.write("Match bigBlind {bb}\n".format(bb=self.big_blind))
        output.flush()

class NoBetLimit(object):
    """Players can bet any amount, at any time"""

    def check_bet(self, pot, bet):
        """Returns true if the bet is legal given the current pot"""
        return bet > 0
