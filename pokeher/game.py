from cards import Hand

"""
Data classes relating to the game of poker
"""


class Match(object):
    """Container for information about a group of games"""
    def reset_match(self):
        self.round = 0
        self.opponents = []
        self.me = None
        self.time_per_move = 500

    def update_match(self):
        if 'your_bot' in self.sharedData:
            self.me = self.sharedData.pop('your_bot')
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

        if 'time_per_move' in self.sharedData:
            time_string = self.sharedData.pop('time_per_move')
            try:
                self.time_per_move = int(time_string)
            except ValueError:
                pass


class Round(object):
    """Memory for a full hand of poker"""
    def reset_round(self):
        self.table_cards = []
        self.hand = None
        self.pot = 0
        self.to_call = 0
        self.bets = {}
        self.big_blind = 0
        self.small_blind = 0
        self.button = None
        self.stacks = {}
        self.preflop_fear = -1

    def update_round(self):
        if 'roundOver' in self.sharedData:
            round_is_over = self.sharedData.pop('roundOver')
            if round_is_over:
                self.reset_round()

        self.parse_blinds()
        self.parse_cards()
        self.parse_pot()
        self.parse_bets()
        self.parse_stacks()

        if 'on_button' in self.sharedData:
            self.button = self.sharedData.pop('on_button')

    def parse_cards(self):
        if hasattr(self, 'me') and self.me:
            key = ('hand', self.me)
            if key in self.sharedData:
                cards = self.sharedData.pop(key)
                self.hand = Hand(cards[0], cards[1])

        if 'table' in self.sharedData:
            self.table_cards = self.sharedData.pop('table')

    def parse_pot(self):
        if 'pot' in self.sharedData:
            pot_str = self.sharedData.pop('pot')
            try:
                self.pot = int(pot_str)
            except ValueError:
                pass

        if 'amount_to_call' in self.sharedData:
            call_str = self.sharedData.pop('amount_to_call')
            try:
                self.to_call = int(call_str)
            except ValueError:
                pass

    def parse_blinds(self):
        if 'small_blind' in self.sharedData:
            sb_string = self.sharedData.pop('small_blind')
            try:
                self.small_blind = int(sb_string)
            except ValueError:
                pass

        if 'big_blind' in self.sharedData:
            bb_string = self.sharedData.pop('big_blind')
            try:
                self.big_blind = int(bb_string)
            except ValueError:
                pass

    def parse_bets(self):
        reset = (self.to_call == 0)
        for bot in self.__get_bots():
            bet_key = ('bet', bot)
            bet = self.sharedData.get(bet_key)
            if reset:
                self.bets[bot] = 0
            elif bet:
                self.bets[bot] = bet

    def parse_stacks(self):
        for bot in self.__get_bots():
            stack_key = ('stack', bot)
            stack = self.sharedData.get(stack_key, "")
            try:
                self.stacks[bot] = int(stack)
            except ValueError:
                self.stacks[bot] = 0

    def __get_bots(self):
        if not hasattr(self, 'opponents') or not self.opponents:
            try:
                return [self.me]
            except AttributeError:
                return []
        return self.opponents + [self.me]


class GameData(Match, Round):
    """Aggregate data classes mixed in together"""
    def __init__(self, sharedData):
        self.sharedData = sharedData
        self.reset()

    def reset(self):
        self.reset_match()
        self.reset_round()

    def update(self):
        self.update_match()
        self.update_round()
