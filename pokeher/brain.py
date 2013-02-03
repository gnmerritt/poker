import cPickle as pickle
import os, time
from game import GameData
from hand_simulator import HandSimulator
from utility import MathUtils

class Brain:
    """The brain: parses lines, combines data classes to make decisions"""
    def __init__(self, bot):
        self.bot = bot
        self.load_realtime_data()
        self.load_precalc_data()
        self.bot.log("Brain started up")

    def load_realtime_data(self):
        sharedData = {}
        self.parser = self.bot.set_up_parser(sharedData, self.do_turn)
        self.data = GameData(sharedData)
        self.data.reset()

    def load_precalc_data(self):
        """Loads pre-computed hand data"""
        infile = os.path.join('data', 'preflop_wins_5000.pickle')
        try:
            in_stream = open(infile, 'r')
            try:
                self.preflop_equity = pickle.load(in_stream)
                self.bot.log("Loaded preflop equity file")
            finally:
                in_stream.close()
        except IOError:
            self.bot.log("IO error loading {f}".format(f=infile))

    def parse_line(self, line):
        """Feeds a line to the parsers"""
        success = self.parser.handle_line(line)
        if success:
            self.data.update()
        else:
            self.bot.log("didn't handle line: " + line + "\n")

    def pot_odds(self):
        """Return the pot odds, or how much we need to gain to call"""
        to_call = self.data.sidepot
        pot_total = to_call + self.data.pot
        return MathUtils.percentage(to_call, pot_total)

    def do_turn(self, timeLeft):
        """Callback for when the brain has to make a decision"""
        if not self.data.hand:
            self.bot.log("No hand, killing ourselves. Data={d}".format(d=self.data))
            self.bot.fold()
            return

        if not self.data.table_cards:
            return self.do_preflop()

        self.bot.fold()

    def do_preflop(self):
        """Preflop hand strategy - random mix of betting, folding, calling"""
        hand = self.data.hand
        equity = self.preflop_equity[repr(hand)]
        pot_odds = self.pot_odds()

        self.bot.log("PF: {h} equity: {e}, pot odds: {p}"
                 .format(h=hand, e=equity, p=pot_odds))

        if equity < 0.3:
            self.bot.fold()
        else:
            self.bot.call(self.data.sidepot)
