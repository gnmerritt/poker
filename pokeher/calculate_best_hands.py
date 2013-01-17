import itertools
import pickle

from cards import Card
from handscore import HandBuilder

class BestHandCalculator(object):
    def run(self):
        self.calculate_best_mapping(6, "six")
        #self.calculate_best_mapping(7, "six")

    def calculate_best_mapping(self, num_cards, name):
        """Iterates through a full deck, 52 choose 7 and maps hands -> best hand
        Naive, has suit included
        """
        deck = Card.full_deck()
        mapping = {}
        counter = 0

        for hand in itertools.combinations(deck, num_cards):
            if counter > 10:
                break
            counter += 1

            (best_hand, score) = HandBuilder(hand).find_hand()
            mapping[hand] = best_hand

        print mapping

if __name__ == '__main__':
    job = BestHandCalculator()
    job.run()
