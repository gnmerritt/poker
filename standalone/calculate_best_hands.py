import itertools
import cPickle as pickle

from cards import Card
from handscore import HandBuilder


class BestHandCalculator(object):

    def run(self):
        self.calculate_best_mapping(6)  # This pickle file is ~750MB
        self.calculate_best_mapping(7)  # This does not complete on my macbook

    def calculate_best_mapping(self, num_cards):
        """Iterates through a full suite
        """
        cards = Card.full_deck()
        mapping = {}

        for hand in itertools.combinations(cards, num_cards):
            (best_hand, score) = HandBuilder(hand).find_hand()
            mapping[hand] = best_hand

        outfile = 'best_hand_{num}.pickle'.format(num=num_cards)
        outf = open(outfile, 'wb')
        pickle.dump(mapping, outf)
        outf.close()

if __name__ == '__main__':
    job = BestHandCalculator()
    job.run()
