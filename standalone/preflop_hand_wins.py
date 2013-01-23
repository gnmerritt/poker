from __future__ import division
import sys, itertools, random, pickle, os, time

sys.path.append('/Users/nathan/sources/poker/')

from pokeher.cards import Card
from pokeher.handscore import *

class PreflopCalculator(object):
    """Estimates the average value, in % of pots won, for a 2 card hole hand.
    Currently only useful for heads up texas hold'em
    """
    TRIES_PER_HAND = 5000 # Should be above 1000
    VERBOSE = False

    def run(self):
        """Calculates the win % for each preflop hand, returns the mapping"""
        cards = Card.full_deck()
        self.wins = {}
        count = 0

        for hand in itertools.combinations(cards, 2):
            wins = 0
            t1 = time.clock()

            for i in range(0, self.TRIES_PER_HAND):
                deck = [c for c in Card.full_deck() if not c in hand]
                equity = self.try_hand(list(hand), deck)
                wins += equity

            percent_pots_won = self.percentage(wins, self.TRIES_PER_HAND)
            self.wins[hand] = percent_pots_won

            print ' {hand} won {percent}% in {tries} tries in {t} seconds' \
                .format(hand=hand,
                        tries=self.TRIES_PER_HAND,
                        percent=percent_pots_won,
                        t=(time.clock() - t1))

            count += 1
            percent_done = self.percentage(count, 1326) # 52 choose 2 == 1326
            print ' Finished hand {c}, {p}% finished' \
                .format(c=count, p=round(percent_done))
            print '-'*10

    def try_hand(self, hand, deck):
        """Returns the percentage of the pot we won with our hand"""
        # Deal out two opponent cards and 5 table cards
        cards = random.sample(deck, 7)
        opponent = cards[0:2]
        table = cards[2:7]

        # Find the best hand for each set of hole cards
        our_hand, our_score = HandBuilder(hand + table).find_hand()
        their_hand, their_score = HandBuilder(opponent + table).find_hand()

        if self.VERBOSE:
            print 'us: {us} and them: {them}'.format(us=our_score, them=their_score)

        # return our equity: fraction of the pot we won
        if our_score > their_score:
            return 1
        elif our_score == their_score:
            return 0.5
        else:
            return 0

    def percentage(self, num, denom):
        return (num / denom) * 100.0

    def save_answer(self):
        """Saves the calculated mapping to a pickle file"""
        outfile = os.path.join('data', 'preflop_wins_{i}.pickle'.format(i=self.TRIES_PER_HAND))
        outf = open(outfile, 'wb')
        pickle.dump(self.wins, outf)
        outf.close()

def calculate():
    job = PreflopCalculator()
    job.run()
    job.save_answer()

if __name__ == '__main__':
    #import cProfile
    #cProfile.run('calculate()', 'hands_profile')
    calculate()
