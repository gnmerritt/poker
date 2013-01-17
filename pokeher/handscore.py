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
        """type should be one of the hand types defined here
        kicker is a tuple of card values sorted based on the hand type
        e.g. kicker=(10,10,9,5,2) for a pair of tens, 9-high
        """
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
        """Returns the best hand & score of length HAND_LENGTH"""
        if not self.cards or len(self.cards) < self.HAND_LENGTH:
            return None
        if len(self.cards) == self.HAND_LENGTH:
            return self.cards

        HandBuilder.sort_hand(self.cards)
        best_hand_score = HandScore()
        best_hand = None
        for hand in itertools.combinations(self.cards, self.HAND_LENGTH):
            score = HandBuilder(list(hand)).score_hand()

            if score > best_hand_score:
                print "{hand} is new best with {score}".format(hand=hand, score=score)
                best_hand_score = score
                best_hand = hand
        return best_hand, best_hand_score

    def score_hand(self):
        """Returns the HandScore of a 5-card hand"""
        score = HandScore()
        if not self.cards or len(self.cards) != self.HAND_LENGTH:
            return score

        HandBuilder.sort_hand(self.cards)

        # Do we have a flush?
        flush_suit = self.select_flush_suit()
        if flush_suit is not None:
            score.type = HandScore.FLUSH

        # Is there a straight?
        if self.is_straight():
            if score.type == HandScore.FLUSH:
                score.type = HandScore.STRAIGHT_FLUSH
            else:
                score.type = HandScore.STRAIGHT

        # At this point, return since we can't have any pairs
        # at the same time as a straight or flush
        if score > HandScore():
            # straights and flushes are both sorted in descending order
            score.kicker = HandBuilder.get_sorted_tuple(self.cards)
            return score

        singles, pairs, trips, quads = HandBuilder.segment_hand(self.cards)

        # Go from least to most valuable hands
        score.type = HandScore.HIGH_CARD

        if pairs:
            score.type = HandScore.PAIR
        if len(pairs) > 2:
            score.type = HandScore.TWO_PAIR
        if trips:
            score.type = HandScore.TRIPS
        if trips and pairs:
            score.type = HandScore.FULL_HOUSE
        if quads:
            score.type = HandScore.QUADS

        score.kicker = self.get_sorted_tuple(singles, [pairs, trips, quads])
        return score

    @staticmethod
    def segment_hand(cards):
        """Splits a hand into 4 lists of pairs, trips, quads and singles"""
        singles = []
        pairs = []
        trips = []
        quads = []
        seen = [None,None] + [0]*13 # card values run 2-15 instead of 0-13

        for card in cards:
            seen[card.value] += 1

        for card_value, times in enumerate(seen):
            target = None
            if times == 1:
                target = singles
            elif times == 2:
                target = pairs
            elif times == 3:
                target = trips
            elif times == 4:
                target = quads

            if times and target is not None:
                for j in range(0, times):
                    target.append(card_value)

        return (singles, pairs, trips, quads)

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

    @staticmethod
    def get_sorted_tuple(singles, ptq=None):
        """Return a sorted hand tuple (by value) so that a tuple comparison
        can be used to evaluate the hand. This handles the default case (sorting
        a straight) as well as if you pass in a list of pairs, triples or quads
          optional argument ptq list of lists: [pairs, trips, quads]
        """
        if ptq is None:
            ptq = [[],[],[]]
        ptq.reverse() # quads > trips > pairs in hand scoring
        ptq.append(singles) # handle the generic case

        def generator():
            for segment in ptq:
                if segment:
                    segment.sort(reverse=True)
                    for c in segment:
                        yield c
        return tuple(generator())

    @staticmethod
    def sort_hand(cards):
        """Sorts a hand, high values first"""
        sort_key = lambda card: card.value
        cards.sort(key=sort_key,reverse=True)

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
