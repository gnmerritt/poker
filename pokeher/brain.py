import cPickle as pickle
import os
from game import *

class Brain:
    """The brain: parses lines, combines data classes to make decisions"""
    def __init__(self, bot):
        self.sharedData = {}
        self.bot = bot
        self.parser = bot.set_up_parser(self.sharedData, self.do_turn)

        self.load_precalc_data()

        # Null-out the data
        self.match = Match(self.sharedData)
        self.player = Player(self.sharedData)
        self.round = Round(self.sharedData)

    def load_precalc_data(self):
        """Loads pre-computed hand data"""
        infile = os.path.join('data', 'preflop_wins_5000.pickle')
        try:
            in_stream = open(infile, 'r')
            try:
                self.preflop_equity = pickle.load(in_stream)
            finally:
                in_stream.close()
        except IOError:
            self.bot.log("IO error loading {f}".format(f=infile))

    def parse_line(self, line):
        """Feeds a line to the parsers"""
        success = self.parser.handle_line(line)
        if success:
            self.update()
        else:
            self.bot.log("didn't handle line: " + line + "\n")

    def do_turn(self, timeLeft):
        """Callback for when the brain has to make a decision"""
        self.bot.call(0)

    def update(self):
        self.match.update()
        self.player.update()
        self.round.update()
