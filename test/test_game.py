import unittest
from pokeher.game import *
from pokeher.theaigame import *

class MatchTest(unittest.TestCase):
    """Tests for the match-level (constant) info"""

    def test_load_opponents_me(self):
        """Tests finding our bot's name and our opponents names"""
        sharedData = {}
        match = Match(sharedData)
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
        match = Match(sharedData)
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
        the_round = Round(sharedData)
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
        self.fail()

class PlayerTest(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
