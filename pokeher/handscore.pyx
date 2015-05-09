from cpython cimport array as c_array
from array import array
cimport cython_util as util
cimport cards
import cards
import itertools


cdef enum:
    NO_SCORE = -1 # when we haven't calculated the score yet
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    TRIPS = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    QUADS = 7
    STRAIGHT_FLUSH = 8


TYPES = ["NONE", "HIGH CARD", "PAIR", "TWO PAIR", "TRIPS", "STRAIGHT", "FLUSH",
         "FULL HOUSE", "QUADS", "STRAIGHT FLUSH"]

cdef class HandScore:
    """The score of a hand. Contains an hand type constant and a value-sorted tuple"""

    def __init__(self, type=NO_SCORE):
        """type should be one of the hand types defined here
        kicker is a tuple of card values sorted based on the hand type
        e.g. kicker=(10,10,9,5,2) for a pair of tens, 9-high
        """
        self.type = type
        self.kicker = None

    def __richcmp__(HandScore self, HandScore other not None, int op):
        cdef int compare
        if self.type > other.type:
            compare = 1
        elif self.type < other.type:
            compare = -1
        else:
            if self.kicker > other.kicker:
                compare = 1
            elif self.kicker < other.kicker:
                compare = -1
            else:
                compare = 0

        return util.richcmp_helper(compare, op)

    def __repr__(self):
        return '{self.type}, {self.kicker}'.format(self=self)

    def __str__(self):
        return "{t}, {k}".format(t=TYPES[self.type + 1], k=self.kicker)

cdef enum:
    HAND_LENGTH = 5

cdef c_array.array int_array_template = array('i', [])

cdef class HandBuilder:
    """Makes the best hand from a given set of cards, scores hands
    """

    def __init__(self, cards):
        if isinstance(cards, tuple):
            self.cards = list(cards)
        else:
            self.cards = cards
        self.length = len(self.cards) if self.cards else 0

    def find_hand(self):
        """Returns the best hand & score of length HAND_LENGTH"""
        if self.length < HAND_LENGTH:
            return None, HandScore()

        best_hand_score = HandScore()
        best_hand = None
        for hand in itertools.combinations(self.cards, HAND_LENGTH):
            score = HandBuilder(list(hand)).score_hand()

            if score > best_hand_score:
                best_hand_score = score
                best_hand = hand
        return best_hand, best_hand_score

    def score_hand(self):
        """Returns the HandScore of a 5-card hand
        This guy runs fast. Don't feed it bad entries"""
        cdef HandScore score
        cdef cards.Card card
        cdef int i
        # card values run 2-15 instead of 0-13
        cdef c_array.array c_seen = c_array.clone(int_array_template, 15, zero=True)

        score = HandScore()
        if self.length == 0:
            return score

        # Find any pairs, triples or quads in the hand and score them
        score.type = HIGH_CARD

        for i in range(self.length):
            card = self.cards[i]
            c_seen[card.value] += 1

        # sort by # of times each value was seen
        # this puts quads in front of triples in front of pairs etc
        # if there aren't any pairs, then this sorts by rank order
        def card_val(cards.Card card):
            cdef int value = card.value
            return (c_seen[value], value)

        self.cards.sort(key=card_val, reverse=True)

        # this function also sets the handscore if there are any pairs etc.
        score.kicker = tuple(self.__score_cards_to_ranks(score))

        # At this point, return since we can't have any pairs
        # at the same time as a straight or flush
        if score.type > HIGH_CARD:
            return score

        # Do we have a flush?
        flush_suit = self.select_flush_suit()
        if flush_suit != -1:
            score.type = FLUSH

        # Is there a straight?
        if self.is_straight():
            if score.type == FLUSH:
                score.type = STRAIGHT_FLUSH
            else:
                score.type = STRAIGHT
            # special case for Ace-low straights :-(
            if score.kicker[0] == 14 and score.kicker[1] == 5:
                score.kicker = (5, 4, 3, 2, 14)

        return score

    cpdef list __score_cards_to_ranks(self, HandScore score):
        """Goes through a list of cards sorted by quad/trip/pair and set the hand score."""
        cdef int last_value, run, i
        cdef cards.Card card
        cdef list results = []

        last_value = -1
        run = 0
        for i in range(self.length):
            card = self.cards[i]
            if card.value == last_value:
                run += 1
            else:
                if run == 4:
                    score.type = QUADS
                elif run == 3:
                    score.type = TRIPS
                elif run == 2:
                    if score.type == TRIPS:
                        score.type = FULL_HOUSE
                    elif score.type == PAIR:
                        score.type = TWO_PAIR
                    else:
                        score.type = PAIR
                run = 1
            last_value = card.value
            results.append(last_value)

        # the full house is the only hand where we need to match on the last card
        if run == 2 and score.type == TRIPS:
            score.type = FULL_HOUSE

        return results

    cpdef bint is_straight(self):
        """returns True if this hand is a straight, false otherwise"""
        cdef int last_value, i, gap, value
        cdef cards.Card card

        last_value = -1
        for i in range(self.length):
            card = self.cards[i]
            value = card.value
            if last_value > 0:
                gap = last_value - value
                # Special case for Ace-low straights (ace is first)
                # these will be sorted A(14)-5-4-3-2
                if gap != 1 and not (last_value == 14 and gap == 9):
                    return False
            last_value = value
        return True

    def cards_to_ranks(self):
        """Returns a generator of the ranks of our cards"""
        cdef cards.Card card
        return (card.value for card in self.cards)

    def sort_hand(self):
        """Sorts a hand, high values first"""
        sort_key = lambda card: card.value
        self.cards.sort(key=sort_key,reverse=True)

    cpdef int select_flush_suit(self):
        """If all cards match suit, return the suit. Return None otherwise."""
        cdef int suit, i
        cdef cards.Card card

        if not self.cards:
            return -1

        suit = self.cards[0].suit
        for i in range(1, self.length):
            card = self.cards[i]
            if suit != card.suit:
                return -1

        return suit
