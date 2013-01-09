import unittest
from pokeher.game import *

class SuitTest(unittest.TestCase):

    def test_eq(self):
        """Makes two instances of each suit and makes sure they're equal"""
        for i in range(0, 3):
            suit1 = Suit(i)
            suit2 = Suit(i)
            self.assertEqual(suit1, suit2)

    def test_bad_suit_values(self):
        for i in range(-1, 12, 5):
            try:
                Suit(i)
            except AssertionError:
                pass
            else:
                self.fail('Suit({value}) allowed'.format(value=i))

class CardTest(unittest.TestCase):

    def test_card_not_suit(self):
        """Tests that the card constructor requires a Suit"""
        try:
            Card(0, 0)
        except AssertionError:
            pass
        else:
            self.fail('Card with non-suit value allowed')

    def test_card_bad_values(self):
        """Tests the card constructor value checks"""
        suit = Suit(0)
        for i in [-1, 15, 232]:
            try:
                Card(i, suit)
            except AssertionError:
                pass
            else:
                self.fail('value {i} allowed'.format(i=i))

    def test_eq(self):
        """Tests the card equals function, and that we can make a full deck"""
        cards = 0
        for i in range(0, 4):
            suit = Suit(i)
            for j in range(2, 15):
                card1 = Card(j, suit)
                card2 = Card(j, suit)
                cards = cards + 1
                self.assertEqual(card1, card2)
        self.assertEqual(cards, 52)

if __name__ == '__main__':
    unittest.main()
