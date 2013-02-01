"""
Data classes relating to the game of poker
"""

class Data(object):
    def __init__(self, sharedData):
        self.sharedData = sharedData
        self.reset()

    def reset(self):
        pass

class Match(Data):
    """Container for information about a group of games"""
    def reset(self):
        self.round = 0
        self.opponents = []
        self.me = None

    def update(self):
        if 'yourBot' in self.sharedData:
            self.me = self.sharedData.pop('yourBot')
            if self.me in self.opponents:
                del self.opponents[self.me]

        if 'round' in self.sharedData:
            round_string = self.sharedData.pop('round')
            try:
                self.round = int(round_string)
            except ValueError:
                pass

        if 'bots' in self.sharedData:
            bot_list = self.sharedData.pop('bots')
            for bot in bot_list:
                if bot == self.me:
                    continue
                self.opponents.append(bot)


class Round(Data):
    """Memory for a full hand of poker"""
    def reset(self):
        self.table_cards = []
        self.hand = None
        self.pot = 0
        self.big_blind = 0
        self.small_blind = 0
        self.button = None

    def update(self):
        self.parse_blinds()
        self.parse_cards()

        if 'onButton' in self.sharedData:
            self.button = self.sharedData.pop('onButton')

    def parse_cards(self):
        pass

    def parse_blinds(self):
        if 'smallBlind' in self.sharedData:
            sb_string = self.sharedData.pop('smallBlind')
            try:
                self.small_blind = int(sb_string)
            except ValueError:
                pass

        if 'bigBlind' in self.sharedData:
            bb_string = self.sharedData.pop('bigBlind')
            try:
                self.big_blind = int(bb_string)
            except ValueError:
                pass

class Player(Data):
    """Player info"""
    def reset(self):
        self.name = None
        self.is_me = False
        self.is_dealer = False
        self.chips = None

    def update(self):
        pass
