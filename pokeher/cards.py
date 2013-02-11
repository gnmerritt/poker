import functools

@functools.total_ordering
class Card(object):
    """Card value - ordinal & suit"""
    FACES = (None,None) + tuple(range(2, 11)) + ("J", "Q", "K", "A")
    SUITS = ("Clubs", "Diamonds", "Hearts", "Spades")

    AIG_FACES = (None,None) + tuple(range(2, 10)) + ("T", "J", "Q", "K", "A")
    AIG_SUITS = ("c", "d", "h", "s")

    __slots__ = ('value', 'suit')
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def is_pair(self, other):
        return self.value == other.value

    def is_suited(self, other):
        return self.suit == other.suit

    def __repr__(self):
        return '{self.value}{self.suit}'.format(self=self)

    def __str__(self):
        return '{value}-{suit}'.format(value=self.FACES[self.value],
                                       suit=self.SUITS[self.suit])

    def aigames_str(self):
        """Returns theaigames card representation"""
        return '{value}{suit}'.format(value=self.AIG_FACES[self.value],
                                       suit=self.AIG_SUITS[self.suit])

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.value == other.value and self.suit == other.suit
        return NotImplemented

    def __lt__(self, other):
        """Implements compare for Cards. Check value, then suit"""
        return ((self.value, self.suit) <
                (other.value, other.suit))

    @staticmethod
    def to_aigames_list(card_list):
        """Converts a list of our card objects into theaigames equivalent"""
        if not card_list:
            return None
        buff = ['[']
        for card in card_list:
            buff.append(card.aigames_str())
            buff.append(',')
        buff[len(buff) - 1] = ']' # replace last ',' with a closing brace
        return "".join(buff)

    @staticmethod
    def full_deck():
        """Returns a full deck of cards"""
        deck = []
        suits = range(0,4)
        for suit in suits:
            cards = (Card(c, suit) for c in range(2,15))
            for card in cards:
                deck.append(card)
        return deck

    @staticmethod
    def one_suit(suit):
        """Returns a single suit in a list"""
        return list(Card(c, suit) for c in range(2,15))

class Hand(object):
    """Player's hand of cards"""
    __slots__ = ('high', 'low')
    def __init__(self, card1, card2):
        if card1 > card2:
            self.high = card1
            self.low = card2
        else:
            self.high = card2
            self.low = card1

    def __repr__(self):
        return '{a}{b}'.format(a=repr(self.high), b=repr(self.low))

    def __str__(self):
        return '{a}, {b}'.format(a=self.high, b=self.low)

    def __eq__(self, other):
        if isinstance(other, Hand):
            return (self.high, self.low) == (other.high, other.low)
        return NotImplemented

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
        return self.card_gap() == 0

class Constants(object):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

    # Can use real numbers for everything else
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
