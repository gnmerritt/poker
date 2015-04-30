cimport cython_random as random
cimport cards
cimport handscore
import cards
from handscore import HandBuilder, HandScore
from handscore cimport HandBuilder, HandScore
from utility import MathUtils

cdef class HandSimulator:
    """Given two hole cards & any number of table cards simulate the
    outcome of the hand a number of times to determine an approximate
    pot equity (percent of pot we can expect to win)
    """
    cdef list hand
    cdef readonly list deck, table_cards
    cdef readonly dict equity

    def __init__(self, cards.Hand hand, table_cards=[], preflop_equity={}):
        self.hand = [hand.high, hand.low]
        self.table_cards = table_cards
        self.equity = preflop_equity
        self.deck = [c for c in cards.full_deck() \
                     if not c in self.table_cards and not c in self.hand]

    def best_hand(self):
        """Returns the best hand possible given the cards the simulator knows about"""
        if len(self.table_cards) >= 3:
            return HandBuilder(self.hand + self.table_cards).find_hand()
        else:
            return self.hand, HandScore()

    def simulate(self, int iterations, int hand_filter=-1):
        """Repeatedly run the simulation, return the % pot equity"""
        cdef int i
        cdef int tries = 0
        cdef float wins = 0

        while iterations - tries > 0:
            for i in xrange(0, iterations - tries):
                result = self.__try_hand(hand_filter)
                if result != -1:
                    wins += result
                    tries += 1

        return MathUtils.percentage(wins, tries)

    cdef float __try_hand(HandSimulator self, int hand_filter):
        """Deal out two opponent cards and 5 table cards"""
        cdef int cards_needed
        cdef handscore.HandScore our_score, their_score

        cdef list cards = random.sample(self.deck, 7)
        cdef list opponent = cards[0:2]

        if hand_filter > 0 and self.equity and \
          not self.passes_filter(opponent[0], opponent[1], hand_filter):
            return -1

        cards_needed = 5 - len(self.table_cards)
        common_cards = cards[2:(2+cards_needed)] + self.table_cards

        # Find the best hand for each set of hole cards
        _, our_score = HandBuilder(self.hand + common_cards).find_hand()
        _, their_score = HandBuilder(opponent + common_cards).find_hand()

        # return our equity: fraction of the pot we won
        if our_score > their_score:
            return 1
        elif our_score == their_score:
            return 0.5
        else:
            return 0

    cpdef bint passes_filter(HandSimulator self, cards.Card card1, cards.Card card2, int hand_filter):
        """Returns true if the hand's preflop equity is greater than the filter value"""
        cdef cards.Card high, low
        if card1.value > card2.value:
            high = card1
            low = card2
        else:
            high = card2
            low = card1
        simple_repr = cards.simple(high, low)
        equity = self.equity.get(simple_repr, 0)
        return equity > hand_filter
