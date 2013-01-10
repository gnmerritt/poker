from pokeher.game import *
from pokeher.game import Constants as C

class CardBuilder:
    """Creates our internal cards from text strings"""

    VALUE_MAP = { 'T': 10, 'J' : C.JACK, 'Q' : C.QUEEN, 'K' : C.KING, 'A' : C.ACE }
    SUIT_MAP = { 'c' : C.CLUBS, 'd' : C.DIAMONDS, 'h' : C.HEARTS, 's' : C.SPADES }

    def from_string(self, string):
        assert len(string) == 2

        value, suit = string[0], string[1]
        mapped_value = self.VALUE_MAP.get(value)
        if not mapped_value:
            mapped_value = int(value)
        mapped_suit = self.SUIT_MAP.get(suit)

        return Card(mapped_value, mapped_suit)

class Parser:
    CARD_REGEXP = r'/\[(.*)\]/';

    def __init__(self, writer, data):
        self._writer = writer
        self._data = data

    def write_line(self, line):
        if line:
            _writer.write(line)
            _writer.flush()

    def handle_line(self, line):
        """Return whether this parser fully handled the input line"""
        return False

class SettingsParser(Parser):
    """
    Parses the following lines from an input stream
      Settings gameType NLHE (ignored)
      Settings gameMode tournament (ignored)
      Settings timeBank 5000
      Settings timePerMove 500
      Settings handsPerLevel 10
      Settings yourBot bot_0

    """
    START_TOKEN = 'Settings'
    YOUR_BOT = 'yourBot'

    def handle_line(self, line):
        if not line:
            return False

        token, key, value = line.split()
        if token != self.START_TOKEN:
            return False

        # For now, only car about name of yourBot
        if key == self.YOUR_BOT:
            self._data[self.YOUR_BOT] = value

        # No other parsers need these lines
        return True


class RoundParser(Parser):
    """
    For Info at the start of every hand
      Match round 1
      Match smallBlind 10
      Match bigBlind 20
      Match onButton bot_0
      bot_0 stack 1500
      bot_1 stack 1500
      bot_0 post 10
      bot_1 post 20
      bot_0 hand [6c,Jc]
    """
    pass

class TurnParser(Parser):
    """
    Info before we have to make a decision
      bot_0 stack 1490
      bot_1 stack 1480
      Match pot 20
      Match sidepots [10]
      go 5000
      Match table [Tc,8d,9c]
    """
    pass
