import sys, itertools, random, pickle
sys.path.append('/Users/nathan/sources/poker/')

from pokeher.cards import Card
from pokeher.handscore import *

class PreflopCalculator(object):
    TRIES_PER_HAND = 1
    VERBOSE = False

    def run(self):
        """Calculates the win % for each preflop hand, returns the mapping"""
        cards = Card.full_deck()
        self.wins = {}
        total_wins = 0
        total_count = 0

        for hand in itertools.combinations(cards, 2):
            self.wins[hand] = 0

            for i in range(0, self.TRIES_PER_HAND):
                if self.try_hand(list(hand)):
                    self.wins[hand] += 1
                    total_wins += 1
                total_count += 1

            if self.VERBOSE:
                print '{hand} won {times}/{tries}, {percent}%' \
                    .format(hand=hand,
                            times=wins[hand],
                            tries=self.TRIES_PER_HAND,
                            percent=self.percentage(self.wins[hand], self.TRIES_PER_HAND))

        print 'Total wins: {p}% (should be ~50%)'.format(p=self.percentage(total_wins, total_count))

    def try_hand(self, hand):
        """returns whether or not the hand we picked won"""
        # Build & shuffle the deck
        deck = [c for c in Card.full_deck() if not c in hand]
        for i in range(0, 7):
            random.shuffle(deck)

        # Deal out two opponent cards and 5 table cards
        opponent = deck[0:2]
        table = deck[2:7]

        our_hand, our_score = HandBuilder(hand + table).find_hand()
        their_hand, their_score = HandBuilder(opponent + table).find_hand()

        if self.VERBOSE:
            print 'us: {us} and them: {them}'.format(us=our_score, them=their_score)

        return our_score > their_score

    def percentage(self, num, denom):
        return round(((num + 0.0) / denom) * 100.0)

    def save_answer(self):
        """Saves the calculated mapping to a pickle file"""
        outfile = 'preflop_wins_{i}.pickle'.format(i=self.TRIES_PER_HAND)
        outf = open(outfile, 'wb')
        pickle.dump(self.wins, outf)
        outf.close()

if __name__ == '__main__':
    job = PreflopCalculator()
    job.run()
    job.save_answer()
