from theaigame import *
from game import *

class Brain:
    """The brain: combines data classes from game.py to make decisions"""
    def __init__(self, input_output):
        self.io = input_output
        self.sharedData = {}
        self.parsers = [ SettingsParser(self.sharedData),
                         RoundParser(self.sharedData),
                         TurnParser(self.sharedData, self.do_turn) ]

        # Null-out the data
        self.match = Match(self.sharedData)
        self.player = Player(self.sharedData)
        self.round = Round(self.sharedData)

    def parse_line(self, line):
        """Feeds a line to the parsers"""
        for parser in self.parsers:
            if parser.handle_line(line):
                return
        self.io.log("didn't handle line: " + line + "\n")

    def do_turn(self, timeLeft):
        """Callback for when the brain has to make a decision"""
        self.update()
        self.io.say('call 0')

    def update(self):
        self.match.update()
        self.player.update()
        self.round.update()
