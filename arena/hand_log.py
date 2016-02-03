import time


class HandLog(object):
    """Keeps track of the events during a hand of poker"""
    TABLE_PLAYER = "TABLE"
    CARDS = "CARDS"
    POT_ANNOUNCE = "POT"
    REMAINING = "REMAINING"

    def __init__(self, bot_stacks):
        self.initial_stacks = bot_stacks
        self.actions = []

    def to_file(self, filename):
        pass  # TODO

    def unix_epoch_s(self):
        return int(time.time())

    def __add(self, who, what, data):
        self.actions.append({
            "ts": self.unix_epoch_s(),
            "player": who,
            "event": what,
            "data": data
        })

    def print_cards(self, cards):
        """"Represents a list of cards as 2 char strings e.g. 'Ad'"""
        return [c.aigames_str() for c in cards]

    def hands(self, hands):
        """"hands: { name: [pokeher.cards.Card] }"""
        for player, cards in hands.items():
            self.__add(player, self.CARDS, self.print_cards(cards))

    def table_cards(self, cards):
        self.__add(self.TABLE_PLAYER, self.CARDS, self.print_cards(cards))

    def action(self, player, action):
        self.__add(player, action.name(), action.amount)

    def pot(self, amount):
        self.__add(self.TABLE_PLAYER, self.POT_ANNOUNCE, amount)

    def remaining(self, players):
        self.__add(self.TABLE_PLAYER, self.REMAINING, players)
