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
    pass

class PlayerTest(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
