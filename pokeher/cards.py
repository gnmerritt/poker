class Suit(object):
    SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]

    def __init__(self, suit):
        assert suit >= 0 and suit < len(self.SUITS)
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

class Card(object):
    """Card value"""
    FACES = [None,None] + range(2, 11) + ["J", "Q", "K", "A"]

    def __init__(self, value, suit):
        assert value > 1
        assert value < len(self.FACES)
        assert isinstance(suit, Suit)

        self.value = value
        self.suit = suit

    def is_pair(self, other):
        return self.value == other.value

    def is_suited(self, other):
        return self.suit == other.suit

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

class Hand(object):
    """Player's hand of cards"""
    def __init__(self, card1, card2):
        if card1.value > card2.value:
            self.high = card1
            self.low = card2
        else:
            self.high = card2
            self.low = card1

    def is_pair(self):
        """Returns true if hand is a pair, false otherwise"""
        return self.high.value == self.low.value

    def is_suited(self):
        """Returns true if other and self are the same suit, false otherwise"""
        return self.high.suit == self.low.suit

    def card_gap(self):
        """Returns the gap between high & low"""
        return (self.high.value - self.low.value) - 1

    def is_connected(self):
        """Returns whether the hand is connected"""
        return self.card_gap() < 1

class HandBuilder(object):
    """Makes the best hand from a given set of cards, scores hands
    """
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    TRIPS = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    QUADS = 7
    STRAIGHT_FLUSH = 8
    def __init__(self, cards):
        self.cards = cards

    def find_hand(self):
        pass

    def select_flush_suit(self):
        """Returns the suit that has 5+ cards, or None otherwise"""
        counts = {}
        for i in range(0, 4):
            counts[i] = 0

        for card in self.cards:
            value = card.suit.suit
            counts[value] = counts[value] + 1

        for suit, count in counts.iteritems():
            if count >= 5:
                return suit
        return None

class Constants(object):
    CLUBS = Suit(0)
    DIAMONDS = Suit(1)
    HEARTS = Suit(2)
    SPADES = Suit(3)

    # Can use real numbers for everything else
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
