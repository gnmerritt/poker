import cPickle as pickle
import sys, itertools, random, os, time

sys.path.append('/Users/nathan/sources/poker/')

import pokeher.cards as c
from pokeher.hand_simulator import HandSimulator
from pokeher.utility import MathUtils

class PreflopCalculator(object):
    """Estimates the average value, in % of pots won, for a 2 card hole hand.
    Currently only useful for heads up texas hold'em
    """
    VERBOSE = False

    def run(self, tries):
        """Calculates the win % for each preflop hand, returns the mapping"""
        cards = c.full_deck()
        self.wins = {}
        self.tries = tries
        count = 0

        for two_cards in itertools.combinations(cards, 2):
            t1 = time.clock()
            hand = c.Hand(two_cards[0], two_cards[1])
            simulator = HandSimulator(hand)
            percent_pots_won = simulator.simulate(tries)

            self.wins[repr(hand)] = percent_pots_won

            print ' {hand} won {percent}% in {tries} tries in {t} seconds' \
                .format(hand=hand,
                        tries=tries,
                        percent=percent_pots_won,
                        t=(time.clock() - t1))

            count += 1
            percent_done = MathUtils.percentage(count, 1326) # 52 choose 2 == 1326
            print ' Finished hand {c} ({p}%)' \
                .format(c=count, p=round(percent_done))
            print '-'*10

    def save_answer(self):
        """Saves the calculated mapping to a pickle file"""
        outfile = os.path.join('data', 'preflop_wins_{i}.pickle'.format(i=self.tries))
        outf = open(outfile, 'wb')
        pickle.dump(self.wins, outf)
        outf.close()

def calculate(tries=5000):
    job = PreflopCalculator()
    job.run(tries)
    job.save_answer()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        argument = sys.argv[1]
        if argument == "profile":
            import cProfile
            from subprocess import call
            cprof_file = os.path.join('data', 'hands_profile')
            calltree_file = os.path.join('data', 'hands_profile.out')
            cProfile.run('calculate(10)', cprof_file)
            call(['pyprof2calltree', '-i', cprof_file, '-o', calltree_file])
            call(['kcachegrind', calltree_file])
        else:
            calculate(int(argument))
    else:
        calculate()
