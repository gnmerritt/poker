from pokeher.game import *
from pokeher.game import Constants as C

class CardBuilder:
    """Creates our internal cards from text strings"""

    VALUE_MAP = { 'T': 10, 'J' : C.JACK, 'Q' : C.QUEEN, 'K' : C.KING, 'A' : C.ACE }
    SUIT_MAP = { 'c' : C.CLUBS, 'd' : C.DIAMONDS, 'h' : C.HEARTS, 's' : C.SPADES }

    def from_string(self, string):
        assert len(string) == 2

        value, suit = string[0], string[1]
        mapped_value = self.VALUE_MAP.get(value)
        if not mapped_value:
            mapped_value = int(value)
        mapped_suit = self.SUIT_MAP.get(suit)

        return Card(mapped_value, mapped_suit)
