import re
from cards import Card
import constants as C
from actions import GameAction
from wiring import Parser, GameParserDelegate


class CardBuilder(object):
    """Creates our internal cards from text strings"""

    VALUE_MAP = {'T': 10, 'J': C.JACK, 'Q': C.QUEEN, 'K': C.KING, 'A': C.ACE}
    SUIT_MAP = {'c': C.CLUBS, 'd': C.DIAMONDS, 'h': C.HEARTS, 's': C.SPADES}

    CARD_REGEXP = r'.*\[(([2-9TJQKA][cdhs],?)+)\].*'

    def from_2char(self, string):
        """Returns a Card from a 2-char token like 9c"""
        if not string or len(string) != 2:
            return None

        value, suit = string[0], string[1]
        mapped_value = self.VALUE_MAP.get(value)
        if not mapped_value:
            mapped_value = int(value)
        mapped_suit = self.SUIT_MAP.get(suit)

        try:
            return Card(mapped_value, mapped_suit)
        except:
            return None

    def from_list(self, token_string):
        """Returns a list of Cards from a string token like [Ah,9d]"""
        if not token_string:
            return None

        match = re.match(self.CARD_REGEXP, (token_string))
        if not match or not match.group(1):
            return None
        cards = match.group(1).split(',')

        results = []
        for card in cards:
            result = self.from_2char(card)
            if result:
                results.append(result)
        return results

    def is_card_list(self, string):
        """Returns true if the string matches the card regexp, or False"""
        if not string:
            return False
        return re.match(self.CARD_REGEXP, string) is not None


class AiGameParser(Parser):
    """Base class for the other STDIN parsers"""
    def handle_line(self, line):
        """Return whether this parser fully handled the input line"""
        if not line:
            return False

        token, key, value = self.__unpack_line(line)
        return self._handle_line(token, key, value)

    def __unpack_line(self, line):
        words = line.split()
        while len(words) < 3:
            words.append("")
        return words[0], words[1], words[2]

    def _handle_line(self, token, key, line):
        return False


class SettingsParser(AiGameParser):
    """
    Parses the following lines from an input stream
      Settings gameType NLHE (ignored)
      Settings gameMode tournament (ignored)
      Settings time_bank 5000 (ignored)
      Settings hands_per_level 10 (ignored)

      Settings time_per_move 500
      bot_0 seat 0
      bot_1 seat 1
      Settings your_bot bot_0
    """
    START_TOKEN = 'Settings'
    HANDLED_KEYS = ['your_bot', 'time_per_move']

    def _handle_line(self, token, key, value):
        # Just pull out any active bots, don't worry about seats yet
        if key in ['seat', 'post']:
            if not 'bots' in self._data:
                self._data['bots'] = [token]
            elif not token in self._data['bots']:
                self._data['bots'].append(token)
            return True

        if token != self.START_TOKEN:
            return False

        if key in self.HANDLED_KEYS:
            self._data[key] = value

        # No other parsers need these lines
        return True


class RoundParser(AiGameParser):
    """
    For Info at the start of every hand
      Match round 1
      Match small_blind 10
      Match big_blind 20
      Match on_button bot_0
    """
    TOKEN = 'Match'
    KEYS = ['round', 'small_blind', 'big_blind', 'on_button']

    def _handle_line(self, token, key, value):
        if token != self.TOKEN:
            return False

        if not key or not key in self.KEYS:
            return False

        self._data[key] = value
        return True


class TurnParser(AiGameParser):
    """
    Info before we have to make a decision
      bot_1 fold 0 (ignored)

      bot_0 stack 1500
      bot_1 stack 1500
      bot_0 post 10
      bot_1 post 20
      bot_0 wins 30
      Match amount_to_call 10
      bot_0 raise 20
      bot_0 check
      bot_0 hand [6c,Jc]
      Match max_win_pot 20
      Match table [Tc,8d,9c]
      Action bot_0 5000
    """
    BOT_DATA = ['raise', 'call', 'wins', 'check', 'hand', 'post', 'stack']
    BET_VERBS = ['raise', 'call', 'post']
    IGNORED_ACTIONS = ['fold']

    def __init__(self, data, goCallback):
        self._data = data
        self._goCallback = goCallback

    def _handle_line(self, token, key, value):
        parser = CardBuilder()
        if parser.is_card_list(value):
            value = parser.from_list(value)

        # check for a 'wins' statement, make note of it
        if key == 'wins':
            self._data['roundOver'] = True

        # Save the data as (key, bot_x) = value
        if key in self.BOT_DATA:
            if not 'bots' in self._data:
                self._data['bots'] = [token]
            else:
                self._data['bots'].append(token)

            if key in self.BET_VERBS:
                try:
                    value_int = int(value)
                except:
                    value_int = 0
                bet_tuple = ('bet', token)
                current_bet = self._data.get(bet_tuple, 0)
                self._data[bet_tuple] = current_bet + value_int
            else:
                self._data[(key, token)] = value
            return True

        # Ignored stuff
        elif key in self.IGNORED_ACTIONS:
            return True

        elif token == 'Match':
            if key == 'max_win_pot':
                self._data['pot'] = value
            else:
                self._data[key] = value
            return True

        elif token == 'Action':
            if self._goCallback:
                try:
                    int_val = int(value)
                except:
                    int_val = 500
                self._goCallback(key, int_val)
                return True

        return False


class TheAiGameParserDelegate(GameParserDelegate):
    def set_up_parser(self, data, turn_callback):
        """Links the workers & callback up from the Brain"""
        self.workers = [SettingsParser(data),
                        RoundParser(data),
                        TurnParser(data, turn_callback), ]
        return self


class TheAiGameActionDelegate(object):
    def bet(self, amount):
        if amount > 0:
            self.say('raise {amount}'.format(amount=amount))
        else:
            self.check()

    def fold(self):
        self.say('fold 0')

    def call(self, amount):
        self.say('call {amount}'.format(amount=amount))

    def check(self):
        self.say('check 0')

    def do_action(self, action):
        """Do a generic GameAction"""
        b = TheAiGameActionBuilder()
        self.say(b.to_string(action))

class TheAiGameActionBuilder(object):
    """Parser for translating actions to/from strings"""
    VERBS = ['fold', 'call', 'raise', 'check']  # Ordered by GameAction

    def from_string(self, input_action_string):
        """Returns the appropriate game action, or None for invalid strings"""
        if not input_action_string:
            return None

        action_string = input_action_string.strip().lower()

        for action_num, verb in enumerate(self.VERBS):
            if action_string.startswith(verb):
                return self.__from_clean_string(action_num, action_string)
        return None

    def __from_clean_string(self, action_num, string):
        """Given a string that starts with a verb, return the GameAction"""
        action = GameAction(action_num)
        words = string.split()
        amount_int = 0

        if words and len(words) > 1:
            amount_str = words[1]
            try:
                amount_int = int(amount_str)
            except ValueError:
                pass
        action.amount = amount_int
        return action

    def to_string(self, action):
        """Given an action, return its theaigames string or None on failure"""
        if not action or action.action < 0 or action.action > len(self.VERBS):
            return None
        action_str = self.VERBS[action.action]
        if action.amount >= 0 and not action.is_fold() and not action.is_check():
            action_str += " {a}".format(a=action.amount)
        return action_str
