import unittest
from pokeher.theaigame import *
import pokeher.cards as cards


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

    def test_to_from_list(self):
        """Tests building lists of cards from a theaigame hand / table token"""
        b = CardBuilder()

        self.assertFalse(b.from_list('asdf2njks92'))

        cases = [([Card(10, C.HEARTS), Card(3, C.DIAMONDS)], '[Th,3d]'),
                 ([Card(3, C.DIAMONDS), Card(10, C.HEARTS)], '[3d,Th]'),
                 ([Card(10, C.CLUBS), Card(8, C.DIAMONDS), Card(9, C.CLUBS)],
                  '[Tc,8d,9c]')]

        for case in cases:
            us, aig_str = case
            self.assertEqual(us, b.from_list(aig_str))
            self.assertEqual(aig_str, cards.to_aigames_list(us))

    def test_all_cards_aig(self):
        """For every card, verify that we can go to/from the aig string"""
        deck = cards.full_deck()
        b = CardBuilder()
        for card in deck:
            card_string = card.aigames_str()
            self.assertEqual(card, b.from_2char(card_string))

    def test_is_card_list(self):
        """Checks that the card builder returns list of card"""
        b = CardBuilder()
        self.assertTrue(b.is_card_list('[Th,3d]'))
        self.assertFalse(b.is_card_list('3nkjnxu903'))
        self.assertFalse(b.is_card_list('[10,22]'))
        self.assertTrue(b.is_card_list('[Qh,Ah,2s,5s,9s]'))

    def test_to_from_aig_format(self):
        """Checks that we can go to/from the AIG format"""
        b = CardBuilder()
        c = Card(10, C.DIAMONDS)
        self.assertEqual(c, b.from_2char(c.aigames_str()))

        c2 = Card(C.ACE, C.HEARTS)
        self.assertEqual(c2, b.from_2char(c2.aigames_str()))
        self.assertNotEqual(c, b.from_2char(c2.aigames_str()))


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
        lines = ['Match round 1',
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
        lines = ['Match pot 20',
                 'bot_0 hand [6c,Jc]',
                 'go 5000',
                 'Match table [Tc,8d,9c]',
                 'bot_1 fold 0',
                 'bot_0 wins 30']

        data = {}
        self.goTime = 0

        def goCallback(time):
            self.goTime = time

        parser = TurnParser(data, goCallback)

        for line in lines:
            self.assertTrue(parser.handle_line(line), 'didnt handle: ' + line)

        self.assertEqual(data['table'], [Card(10, C.CLUBS),
                                         Card(8, C.DIAMONDS),
                                         Card(9, C.CLUBS)])
        self.assertEqual(data['pot'], str(20))
        self.assertEqual(data[('hand', 'bot_0')], [Card(6, C.CLUBS),
                                                   Card(C.JACK, C.CLUBS)])
        self.assertEqual(self.goTime, 5000)
        self.assertEqual(data[('wins', 'bot_0')], str(30))


class MockTalker(object):
    def say(self, string):
        self.last_string = string


class TestableTheAiGameActionDelegate(TheAiGameActionDelegate, MockTalker):
    pass


class ActionDelegateTest(unittest.TestCase):

    def test_specific_actions(self):
        d = TestableTheAiGameActionDelegate()
        self.assertTrue(d)
        d.call(100)
        self.assertEqual('call 100', d.last_string)

        d.fold()
        self.assertEqual('fold 0', d.last_string)

        d.bet(100)
        self.assertEqual('raise 100', d.last_string)

    def test_generic_actions(self):
        d = TestableTheAiGameActionDelegate()
        b = TheAiGameActionBuilder()
        actions = ['call 0',
                   'raise 390',
                   'check',
                   'fold']
        for action_str in actions:
            action = b.from_string(action_str)
            d.do_action(action)
            self.assertEqual(action_str, d.last_string)


class ActionBuilderTest(unittest.TestCase):

    def test_parse_actions(self):
        """Tests parsing out actions & amounts"""
        b = TheAiGameActionBuilder()
        actions = [['call 0', 1, 0],
                   ['raise 390', 2, 390],
                   ['check 0', 3, 0],
                   ['fold 3902', 0, 3902],
                   ['FOLD', 0, 0],
                   ['   raise  30203   ', 2, 30203],
                   ['fold', 0, 0],
                   ['call 100 100', 1, 100]]

        for action_set in actions:
            a = b.from_string(action_set[0])
            self.assertTrue(a)
            self.assertEqual(a.action, action_set[1])
            self.assertEqual(a.amount, action_set[2])

    def test_garbage_actions(self):
        """Makes sure the action parser can handle garbage input"""
        b = TheAiGameActionBuilder()
        actions = ['caasdfll 0',
                   '0 raise 390',
                   '02 check 0 20 1910 30',
                   'this\n fold',
                   None,
                   '']

        for action_string in actions:
            a = b.from_string(action_string)
            self.assertFalse(a, "string pased: {s}".format(s=action_string))

    def test_bad_action_amount(self):
        """Checks bad number in second position"""
        b = TheAiGameActionBuilder()
        check = b.from_string('check forty')
        self.assertTrue(check)
        self.assertEqual(check.action, 3)
        self.assertEqual(check.amount, 0)

    def test_to_from_strings(self):
        """Converts actions from a string then back"""
        b = TheAiGameActionBuilder()
        actions = ['call 0',
                   'raise 390',
                   '  check',
                   'fold',
                   'raise 30203    ',
                   '   fold',
                   'call 100']
        for action_str in actions:
            action = b.from_string(action_str)
            clean_string = action_str.strip().lower()
            self.assertTrue(action)
            self.assertEqual(b.to_string(action), clean_string,
                             "saw {to} needed {s} from/to action string"
                             .format(s=clean_string, to=b.to_string(action)))

    def test_to_string_edges(self):
        """Tests the fail cases of to string"""
        b = TheAiGameActionBuilder()
        self.assertFalse(b.to_string(None))

        bad_action = GameAction(-9)
        self.assertFalse(b.to_string(bad_action))

if __name__ == '__main__':
    unittest.main()
