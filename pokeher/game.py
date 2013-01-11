"""
Data classes relating to the game of poker
"""

class Data(object):
    def __init__(self, sharedData):
        self.data = sharedData

class Match(Data):
    """Container for information about a group of games"""
    def update(self):
        self.round = 0
        self.opponents = []
        self.me = None

class Round(Data):
    """Memory for a full hand of poker"""
    def update(self):
        self.table_cards = []
        self.hand = None
        self.pot = 0
        self.big_blind = 0
        self.small_blind = 0

class Player(Data):
    """Player info"""
    def update(self):
        self.name = None
        self.is_me = False
        self.is_dealer = False
        self.chips = None
