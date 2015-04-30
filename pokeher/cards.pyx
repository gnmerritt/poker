cimport cython_util as util

cdef class Card:
    """Card value - ordinal & suit"""
    FACES = (None,None) + tuple(range(2, 11)) + ("J", "Q", "K", "A")
    SUITS = ("Clubs", "Diamonds", "Hearts", "Spades")

    AIG_FACES = (None,None) + tuple(range(2, 10)) + ("T", "J", "Q", "K", "A")
    AIG_SUITS = ("c", "d", "h", "s")

    def __cinit__(self, int val, int s):
        self.value = val
        self.suit = s

    def is_pair(self, Card other):
        return self.value == other.value

    def is_suited(self, Card other):
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

    def __richcmp__(Card self, Card other not None, int op):
        """Cython equivalent of functools.totalordering
        Implements compare for Cards. Check value, then suit"""
        cdef int compare
        if self.value > other.value:
            compare = 1
        elif self.value < other.value:
            compare = -1
        else:
            if self.suit > other.suit:
                compare = 1
            elif self.suit < other.suit:
                compare = -1
            else:
                compare = 0
        return util.richcmp_helper(compare, op)

"""Functions for generating lists of cards
"""

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

def full_deck():
    """Returns a full deck of cards"""
    cdef int suit, c

    deck = []
    for suit in range(0,4):
        for c in range(2,15):
            deck.append(Card(c, suit))
    return deck

def one_suit(int suit):
    """Returns a single suit in a list"""
    cdef int c
    return list(Card(c, suit) for c in range(2,15))

cpdef simple(Card high, Card low):
    """Returns a simplified representation of a hand which ignores
    individual suits and only checks suited/unsuited"""
    cdef char* suited = "s" if high.suit == low.suit else "u"
    return "{hv}{lv}{s}".format(hv=high.value, lv=low.value, s=suited)


cdef class Hand:
    """Player's hand of cards"""
    def __init__(self, Card card1, Card card2):
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

    def __richcmp__(Hand self, Hand other not None, int op):
        if self.high > other.high:
            compare = 1
        elif self.high < other.high:
            compare = -1
        else:
            if self.low > other.low:
                compare = 1
            elif self.low < other.low:
                compare = -1
            else:
                compare = 0
        return util.richcmp_helper(compare, op)

    cpdef simple(self):
        return simple(self.high, self.low)

    cpdef bint is_pair(self):
        """Returns true if hand is a pair, false otherwise"""
        return self.high.value == self.low.value

    cpdef bint is_suited(self):
        """Returns true if other and self are the same suit, false otherwise"""
        return self.high.suit == self.low.suit

    cpdef int card_gap(self):
        """Returns the gap between high & low"""
        return (self.high.value - self.low.value) - 1

    cpdef bint is_connected(self):
        """Returns whether the hand is connected"""
        return self.card_gap() == 0
