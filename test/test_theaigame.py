import unittest
from pokeher.game import *
from pokeher.game import Constants as C
from pokeher.theaigame import *

class CardBuilderTest(unittest.TestCase):
    def test_from_string(self):
        """Tests building our cards from theaigame text strings"""
        b = CardBuilder()

        self.assertEqual(b.from_string('Th'), Card(10, C.HEARTS))
        self.assertEqual(b.from_string('9s'), Card(9, C.SPADES))
        self.assertEqual(b.from_string('Ad'), Card(C.ACE, C.DIAMONDS))
        self.assertEqual(b.from_string('2c'), Card(2, C.CLUBS))
