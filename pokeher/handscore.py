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
        if isinstance(cards, tuple):
            self.cards = list(cards)
        else:
            self.cards = cards

    def find_hand(self):
        """Returns the best hand & score of length HAND_LENGTH"""
        if not self.cards or len(self.cards) < self.HAND_LENGTH:
            return None, None

        best_hand_score = HandScore()
        best_hand = None
        for hand in itertools.combinations(self.cards, self.HAND_LENGTH):
            score = HandBuilder(list(hand)).score_hand()

            if score > best_hand_score:
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
        if score.type > HandScore.NO_SCORE:
            # straights and flushes are both sorted in descending order
            score.kicker = tuple(self.cards_to_ranks())
            return score

        return self.__score_hand(score)

    def __score_hand(self, score):
        """Scores a hand, finding pairs, trips & quads and setting the kicker"""
        singles = None
        pairs = None
        trips = None
        quads = None
        score.type = HandScore.HIGH_CARD

        def up_score(new):
            if new > score.type:
                score.type = new

        seen = [None,None] + [0]*13 # card values run 2-15 instead of 0-13
        for card in self.cards:
            seen[card.value] += 1

        for card_value, times in enumerate(seen):
            if times == 1:
                if not singles:
                    singles = [card_value]
                else:
                    singles.append(card_value)
            elif times == 2:
                if not pairs:
                    pairs = [card_value]
                    up_score(HandScore.PAIR)
                else:
                    if card_value > pairs[0]:
                        pairs.insert(0, card_value)
                    else:
                        pairs.append(card_value)
                    up_score(HandScore.TWO_PAIR)
            elif times == 3:
                trips = card_value
                up_score(HandScore.TRIPS)
            elif times == 4:
                quads = card_value
                up_score(HandScore.QUADS)

        # have to find the full house separately
        if pairs and trips:
            up_score(HandScore.FULL_HOUSE)

        def kicker_generator():
            if quads:
                yield quads
            if trips:
                yield trips
            if pairs:
                for x in pairs:
                    yield x
            if singles:
                singles.sort(reverse=True)
                for x in singles:
                    yield x

        score.kicker = tuple(kicker_generator())
        return score

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

    def cards_to_ranks(self):
        """Returns a generator of the ranks of our cards"""
        return (card.value for card in self.cards)

    @staticmethod
    def sort_hand(cards):
        """Sorts a hand, high values first"""
        sort_key = lambda card: card.value
        cards.sort(key=sort_key,reverse=True)

    def __gap(self, card1, card2):
        return card1.value - card2.value

    def select_flush_suit(self):
        """If all cards match suit, return the suit. Return None otherwise."""
        if not self.cards:
            return None

        suit = self.cards[0].suit.suit
        for card in self.cards:
            value = card.suit.suit
            if suit != value:
                return None

        return suit
