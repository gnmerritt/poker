"""
Stuff to play the actual game of poker
"""

class Suit:
    SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]

    def __init__(self, suit):
        self.suit = suit

    def __repr__(self):
        return self.SUITS[self.suit]

    def __eq__(self, other):
        if isinstance(other, Suit):
            return self.suit == other.suit
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

class Card:
    """Card value"""

    FACES = [None,None] + range(2,10) + ["J", "Q", "K", "A"]

    def __init__(self, value, suit):
        assert value > 1
        assert value < len(self.FACES)

        self.value = value
        self.suit = suit

    def __repr__(self):
        return '{value}-{suit}'.format(value=self.FACES[self.value], suit=str(self.suit))

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.value == other.value and self.suit == other.suit
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

class Hand:
    """Player's hand of cards"""
    def __init__(self, cards):
        self.cards = cards

    def score(self):
        """Calculates the score of this hand"""
        return 0

class Game:
    """Memory for a full hand of poker"""
    pass

class Match:
    """Container for information about a group of games"""
    pass
