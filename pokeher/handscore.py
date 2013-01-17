import functools
import itertools

@functools.total_ordering
class HandScore(object):
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

    def __init__(self, type=NO_SCORE, kicker=NO_SCORE):
        self.type = type
        self.kicker = kicker

    def __eq__(self, other):
        return (self.type, self.kicker) == \
            (other.type, other.kicker)

    def __lt__(self, other):
        return (self.type, self.kicker) < \
            (other.type, other.kicker)

    def __repr__(self):
        return '{self.type}, {self.kicker}'.format(self=self)

class HandBuilder(object):
    """Makes the best hand from a given set of cards, scores hands
    """
    HAND_LENGTH = 5

    def __init__(self, cards):
        self.cards = cards

    def find_hand(self):
        """Returns the best hand of length HAND_LENGTH"""
        if not self.cards or len(self.cards) < self.HAND_LENGTH:
            return None
        if len(self.cards) == self.HAND_LENGTH:
            return self.cards

        self.__sort_hand()
        best_hand_score = HandScore()
        best_hand = None
        for hand in itertools.combinations(self.cards, self.HAND_LENGTH):
            score = HandBuilder(hand).__score_hand()

            if score > best_hand_score:
                print "{hand} is new best with {score}".format(hand=hand, score=score)
                best_hand_score = score
                best_hand = hand
        return best_hand

    def score_hand(self):
        """Returns the score of a 5-card hand"""
        # Drop invalid hands
        if not self.cards or len(self.cards) != self.HAND_LENGTH:
            return HandScore(HandScore.NO_SCORE)
        self.__sort_hand()
        return self.__score_hand()

    def __score_hand(self):
        """Internal verson of score_hand, works on tuples and lists
        Assumes that self.cards is already sorted"""
        score = HandScore()

        # Do we have a flush?
        flush_suit = self.select_flush_suit()
        if flush_suit is not None:
            # Add the values of all the cards to distinguish between flushes
            score.type = HandScore.FLUSH

        # Is there a straight?
        if self.is_straight():
            if score.type == HandScore.FLUSH:
                score.type = HandScore.STRAIGHT_FLUSH
            else:
                score.type = HandScore.STRAIGHT
            # Add the high card to distinguish between multiple straights

        # At this point, return since we can't have any pairs
        # at the same time as a straight or flush
        if score > HandScore():
            return score

        pairs, trips, quads = self.find_pairs_trips_quads()

        # Go from least to most valuable hands
        score.type = HandScore.HIGH_CARD

        if pairs:
            score.type = HandScore.PAIR
        if len(pairs) > 1:
            score.type = HandScore.TWO_PAIR
        if trips:
            score.type = HandScore.TRIPS
        if trips and pairs:
            score.type = HandScore.FULL_HOUSE
        if quads:
            score.type = HandScore.QUADS

        return score

    def find_pairs_trips_quads(self):
        """Finds pairs and trips, returns a list of pairs & a list of trips"""
        pairs = []
        trips = []
        quads = []
        seen = [None,None] + [0]*13 # card values run 2-15 instead of 0-13

        for card in self.cards:
            seen[card.value] += 1

        for i, val in enumerate(seen):
            if val == 2:
                pairs.append(i)
            elif val == 3:
                trips.append(i)
            elif val == 4:
                quads.append(i)

        return (pairs, trips, quads)

    def is_straight(self):
        """returns True if this hand is a straight, false otherwise"""
        last_card = None
        for card in self.cards:
            if last_card:
                gap = self.__gap(last_card, card)
                if gap != 1:
                    return False
            last_card = card
        return True

    def __sort_hand(self):
        """Sorts a hand, high values first"""
        sort_key = lambda card: (card.value, card.suit.suit)
        self.cards.sort(key=sort_key,reverse=True)

    def __gap(self, card1, card2):
        return card1.value - card2.value

    def select_flush_suit(self):
        """Returns the suit that has 5+ cards, or None otherwise"""
        if not self.cards:
            return None

        counts = {}
        for i in range(0, 4):
            counts[i] = 0

        for card in self.cards:
            value = card.suit.suit
            counts[value] += 1

        for suit, count in counts.iteritems():
            if count >= self.HAND_LENGTH:
                return suit
        return None
