import re
from cards import *
from cards import Constants as C

class CardBuilder:
    """Creates our internal cards from text strings"""

    VALUE_MAP = { 'T': 10, 'J' : C.JACK, 'Q' : C.QUEEN, 'K' : C.KING, 'A' : C.ACE }
    SUIT_MAP = { 'c' : C.CLUBS, 'd' : C.DIAMONDS, 'h' : C.HEARTS, 's' : C.SPADES }

    CARD_REGEXP = r'.*\[([2-9TJQKAcdhs,]+)\].*'

    def from_2char(self, string):
        """Returns a Card from a 2-char token like 9c"""
        if not string or len(string) != 2:
            return None

        value, suit = string[0], string[1]
        mapped_value = self.VALUE_MAP.get(value)
        if not mapped_value:
            mapped_value = int(value)
        mapped_suit = self.SUIT_MAP.get(suit)

        return Card(mapped_value, mapped_suit)

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
        """Returns true if the string matches the card regexp, false otherwise"""
        if not string:
            return False
        return re.match(self.CARD_REGEXP, string) is not None

class Parser:
    """Base class for the other STDIN parsers"""
    def __init__(self, data):
        self._data = data

    def handle_line(self, line):
        """Return whether this parser fully handled the input line"""
        if not line:
            return False

        # Special case: make 'go 5000 -> go go 5000'
        if line.startswith('go '):
            line = 'go ' + line

        token, key, value = line.split()
        return self._handle_line(token, key, value)

    def _handle_line(self, token, key, line):
        return False

    def is_bot_directive(self, token):
        if token.startswith('bot_'):
           return True
        return False

class SettingsParser(Parser):
    """
    Parses the following lines from an input stream
      Settings gameType NLHE (ignored)
      Settings gameMode tournament (ignored)
      Settings timeBank 5000 (ignored)
      Settings timePerMove 500 (ignored)
      Settings handsPerLevel 10 (ignored)
      bot_0 seat 0 (ignored)
      bot_1 seat 1 (ignored)

      Settings yourBot bot_0
    """
    START_TOKEN = 'Settings'
    YOUR_BOT = 'yourBot'

    def _handle_line(self, token, key, value):
        if self.is_bot_directive(token) and key == 'seat':
            return True

        if token != self.START_TOKEN:
            return False

        # For now, only car about name of yourBot
        if key == self.YOUR_BOT:
            self._data[key] = value

        # No other parsers need these lines
        return True


class RoundParser(Parser):
    """
    For Info at the start of every hand
      Match round 1
      Match smallBlind 10
      Match bigBlind 20
      Match onButton bot_0
    """
    TOKEN = 'Match'
    KEYS = ['round', 'smallBlind', 'bigBlind', 'onButton']

    def _handle_line(self, token, key, value):
        if token != self.TOKEN:
            return False

        if not key or not key in self.KEYS:
            return False

        self._data[key] = value
        return True

class TurnParser(Parser):
    """
    Info before we have to make a decision
      bot_0 stack 1500 (ignored)
      bot_1 stack 1500 (ignored)
      bot_0 post 10 (ignored)
      bot_1 post 20 (ignored)
      Match sidepots [10] (ignored)
      bot_1 fold 0 (ignored)
      bot_0 wins 30 (ignored)

      bot_0 raise 20
      bot_0 hand [6c,Jc]
      Match pot 20
      Match table [Tc,8d,9c]
      go 5000 (transformed into go go 5000)
    """
    BOT_DATA = ['raise', 'call', 'wins', 'check', 'hand']
    IGNORED_ACTIONS = ['fold']

    def __init__(self, data, goCallback):
        self._data = data
        self._goCallback = goCallback

    def _handle_line(self, token, key, value):
        parser = CardBuilder()
        if parser.is_card_list(value):
            value = parser.from_list(value)

        # Save the data as (key, bot_x) = value
        if self.is_bot_directive(token) and key in self.BOT_DATA:
            self._data[(key, token)] = value
            return True

        # Ignored stuff
        elif self.is_bot_directive(token) and key in self.IGNORED_ACTIONS:
            return True

        elif token == 'Match':
            self._data[key] = value
            return True
        elif token == 'go':
            if self._goCallback:
                self._goCallback(int(value))
                return True

        return False
