import sys
import unittest
from pokeher.cards import *
from pokeher.cards import Constants as C
from pokeher.theaigame import *

class CardBuilderTest(unittest.TestCase):
    def test_from_string(self):
        """Tests building our cards from theaigame text strings"""
        b = CardBuilder()

        self.assertFalse(b.from_2char(None))
        self.assertFalse(b.from_2char('Thh'))
        self.assertFalse(b.from_2char('T'))

        self.assertEqual(b.from_2char('Th'), Card(10, C.HEARTS))
        self.assertEqual(b.from_2char('9s'), Card(9, C.SPADES))
        self.assertEqual(b.from_2char('Ad'), Card(C.ACE, C.DIAMONDS))
        self.assertEqual(b.from_2char('2c'), Card(2, C.CLUBS))

    def test_from_list(self):
        """Tests building a list of cards from a theaigame hand or table token"""
        b = CardBuilder()

        self.assertFalse(b.from_list(None))
        self.assertFalse(b.from_list('asdf2njks92'))

        answer1 = [Card(10, C.HEARTS), Card(3, C.DIAMONDS)]
        self.assertEqual(b.from_list('[Th,3d]'), answer1)
        answer1.reverse()
        self.assertEqual(b.from_list('[3d,Th]'), answer1)

        answer2 = [Card(10, C.CLUBS), Card(8, C.DIAMONDS), Card(9, C.CLUBS)]
        self.assertEqual(b.from_list(' [Tc,8d,9c]   '), answer2)

    def test_is_card_list(self):
        b = CardBuilder()
        self.assertTrue(b.is_card_list('[Th,3d]'))
        self.assertFalse(b.is_card_list('3nkjnxu903'))

class SettingsParserTest(unittest.TestCase):
    def test_parse_settings(self):
        """Tests that the beginning settings are passed to the data model"""
        lines = ['Settings gameType NLHE',
                 'Settings gameMode tournament',
                 'Settings timeBank 5000',
                 'Settings timePerMove 500',
                 'Settings handsPerLevel 10',
                 'Settings yourBot bot_0',
                 'bot_0 seat 0',
                 'bot_1 seat 1']

        data = {}
        parser = SettingsParser(data)

        for line in lines:
            handled = parser.handle_line(line)
            self.assertTrue(handled)

        self.assertEqual(data['yourBot'], 'bot_0')

class RoundParserTest(unittest.TestCase):
    def test_parse_settings(self):
        """Tests round by round parsing settings"""
        lines = [ 'Match round 1',
                  'Match smallBlind 10',
                  'Match bigBlind 20',
                  'Match onButton bot_0']

        data = {}
        parser = RoundParser(data)

        for line in lines:
            self.assertTrue(parser.handle_line(line))

        self.assertEqual(str(10), data['smallBlind'])
        self.assertEqual(str(20), data['bigBlind'])
        self.assertEqual('bot_0', data['onButton'])

class TurnParserTest(unittest.TestCase):
    def test_parse_settings(self):
        """Tests parsing info that indicates we need to make a decision"""
        lines = [ 'Match pot 20',
                  'bot_0 hand [6c,Jc]',
                  'go 5000',
                  'Match table [Tc,8d,9c]',
                  'bot_1 fold 0',
                  'bot_0 wins 30' ]

        data = {}
        self.goTime = 0
        def goCallback(time):
            self.goTime = time

        parser = TurnParser(data, goCallback)

        for line in lines:
            self.assertTrue(parser.handle_line(line), 'didnt handle: ' + line)

        self.assertEqual(data['table'], [Card(10, C.CLUBS), Card(8, C.DIAMONDS), Card(9, C.CLUBS)])
        self.assertEqual(data['pot'], str(20))
        self.assertEqual(data[('hand', 'bot_0')], [Card(6, C.CLUBS), Card(C.JACK, C.CLUBS)])
        self.assertEqual(self.goTime, 5000)
        self.assertEqual(data[('wins', 'bot_0')], str(30))

if __name__ == '__main__':
    unittest.main()
