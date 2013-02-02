import unittest
from pokeher.cards import *
from pokeher.game import *
from pokeher.theaigame import *

class MatchTest(unittest.TestCase):
    """Tests for the match-level (constant) info"""

    def test_load_opponents_me(self):
        """Tests finding our bot's name and our opponents names"""
        sharedData = {}
        match = GameData(sharedData)
        parser = SettingsParser(sharedData)
        lines = ['bot_0 seat 0',
                 'bot_1 seat 1',
                 'bot_4 seat 3',
                 'Settings yourBot bot_0']
        for line in lines:
            self.assertTrue(parser.handle_line(line))
        match.update()

        self.assertTrue(match, "match instantiated")
        self.assertEqual(match.me, "bot_0")
        self.assertTrue(match.opponents)
        self.assertTrue('bot_1' in match.opponents)
        self.assertTrue('bot_4' in match.opponents)
        self.assertFalse('bot_0' in match.opponents)

    def test_round(self):
        """Tests getting the current round"""
        sharedData = {}
        match = GameData(sharedData)
        parser = RoundParser(sharedData)
        self.assertEqual(match.round, 0)
        self.assertTrue(parser.handle_line('Match round 8'))
        match.update()
        self.assertEqual(match.round, 8)

        self.assertTrue(parser.handle_line('Match round 8392'))
        match.update()
        self.assertEqual(match.round, 8392)
        self.assertTrue(parser.handle_line('Match round lkfashfas'))
        self.assertEqual(match.round, 8392) # shouldn't change or explode

class RoundTest(unittest.TestCase):
    """Tests for round by round stuff - cards and bots and blinds etc"""

    def test_blinds_button(self):
        """Test getting the blind and button"""
        sharedData = {}
        the_round = GameData(sharedData)
        parser = RoundParser(sharedData)
        lines = ['Match smallBlind 10',
                 'Match bigBlind 20',
                 'Match onButton bot_0']

        for line in lines:
            self.assertTrue(parser.handle_line(line))
        the_round.update()

        self.assertEqual(the_round.small_blind, 10)
        self.assertEqual(the_round.big_blind, 20)
        self.assertEqual(the_round.button, 'bot_0')

    def test_cards(self):
        """Tests finding the cards"""
        sharedData = {}
        data = GameData(sharedData)
        data.me = 'bot_0'
        callback = None
        parser = TurnParser(sharedData, callback)
        lines = ['bot_0 hand [6c,Jc]',
                 'Match pot 20',
                 'Match table [Tc,8d,9c]',
                 'Match sidepots [10]']

        for line in lines:
            self.assertTrue(parser.handle_line(line))
        data.update()

        self.assertEqual(data.hand,
                         Hand(Card(6, C.CLUBS), Card(C.JACK, C.CLUBS)))
        self.assertEqual(data.table_cards, [Card(10, C.CLUBS), Card(8, C.DIAMONDS), Card(9, C.CLUBS)])
        self.assertEqual(data.pot, 20)
        self.assertEqual(data.sidepot, 10)

        parser.handle_line('bot_0 wins 90')
        data.update()
        self.assertFalse(data.hand)
        self.assertEqual(data.pot, 0)

if __name__ == '__main__':
    unittest.main()
