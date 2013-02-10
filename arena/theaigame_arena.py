from holdem import Holdem
from betting import Blinds, NoBetLimit

class TheAiGameArena(Holdem, Blinds, NoBetLimit):
    """Arena for testing bots for http://theaigames.com
    Rules are heads-up, no limit hold'em"""
    def __init__(self):
        pass
