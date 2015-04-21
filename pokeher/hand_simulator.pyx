try:
    import random
except:
    import fake_random as random
cimport cards
cimport handscore
import cards
from handscore import HandBuilder
from handscore cimport HandBuilder
from utility import MathUtils

cdef class HandSimulator:
    """Given two hole cards & any number of table cards simulate the
    outcome of the hand a number of times to determine an approximate
    pot equity (percent of pot we can expect to win)
    """
    cdef object hand
    cdef readonly object deck, table_cards

    def __init__(self, hand, table_cards=[]):
        self.hand = [hand.high, hand.low]
        self.table_cards = table_cards
        self.deck = [c for c in cards.full_deck() \
                     if not c in self.table_cards and not c in self.hand]

    def best_hand(self):
        """Returns the best hand possible given the cards the simulator knows about"""
        if len(self.table_cards) >= 3:
            return HandBuilder(self.hand + self.table_cards).find_hand()
        else:
            return self.hand

    def simulate(self, int iterations):
        """Repeatedly run the simulation, return the % pot equity"""
        cdef int i
        cdef float wins
        wins = 0

        for i in xrange(0, iterations):
            wins += self.__try_hand()

        return MathUtils.percentage(wins, iterations)

    def __try_hand(self):
        """Deal out two opponent cards and 5 table cards"""
        cdef int cards_needed
        cdef handscore.HandScore our_score, their_score

        cards = random.sample(self.deck, 7)
        opponent = cards[0:2]

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
