import math
from cards import *
from cards import Constants as C

class ChenScore:
    """ Scores a hand according to the Chen forumula.
    See: http://www.thepokerbank.com/strategy/basic/starting-hand-selection/chen-formula/
    """
    CARD_TO_POINTS = { C.ACE : 10, C.KING : 8, C.QUEEN : 7, C.JACK : 6 }
    GAP_MINUS_POINTS = { 1 : -1, 2 : -2, 3 : -4 }

    def __init__(self, hand):
        self.hand = hand

    def score(self):
        """Scores a hand based on the Chen system"""
        points = self.points_for_card(self.hand.high)

        # For a pair, return double the high cards value
        if self.hand.is_pair():
            return max(points * 2, 5)

        # Add two points if the cards are suited
        if self.hand.is_suited():
            points = points + 2

        # Subtract points if there is a gap between the two cards
        if not self.hand.is_connected():
            gap_penalty = self.GAP_MINUS_POINTS.get(self.hand.card_gap())
            if not gap_penalty:
                gap_penalty = -5

            points = points + gap_penalty

        # Add 1 point if there is a 0 or 1 card gap and both cards < Q
        if self.hand.high.value < C.QUEEN and \
                self.hand.is_connected() or self.hand.card_gap() == 1:
            points = points + 1

        return math.ceil(points)

    def points_for_card(self, card):
        points = self.CARD_TO_POINTS.get(card.value)
        if not points:
            points = card.value * 0.5
        return points
