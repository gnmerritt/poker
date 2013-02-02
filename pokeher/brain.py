import cPickle as pickle
import os
from game import GameData

class Brain:
    """The brain: parses lines, combines data classes to make decisions"""
    def __init__(self, bot):
        self.bot = bot
        self.load_realtime_data()
        self.load_precalc_data()

    def load_realtime_data(self):
        sharedData = {}
        self.parser = self.bot.set_up_parser(sharedData, self.do_turn)
        self.data = GameData(sharedData)
        self.data.reset()

    def load_precalc_data(self):
        """Loads pre-computed hand data"""
        infile = os.path.join('data', 'preflop_wins_100.pickle')
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
            self.data.update()
        else:
            self.bot.log("didn't handle line: " + line + "\n")

    def do_turn(self, timeLeft):
        """Callback for when the brain has to make a decision"""
        if not self.data.hand:
            self.log("No hand, killing ourselves")
            self.bot.fold()
            return

        if not self.data.table_cards:
            return self.do_preflop()

        cards = self.data.table_cards

        if len(cards) == 3:
            return self.do_third()
        elif len(cards) == 4:
            return self.do_fourth()
        else:
            return self.do_fifth()

    def do_preflop(self):
        """Preflop hand strategy"""
        hand = self.data.hand
        equity = self.preflop_equity[repr(hand)]

        if equity < 0.3:
            self.bot.fold()
        else:
            self.bot.call(self.data.sidepot)

    def do_third(self):
        pass

    def do_fourth(self):
        pass

    def do_fifth(self):
        pass
