from __future__ import division
import cPickle as pickle
import os, time, random

from game import GameData
from hand_simulator import HandSimulator
from utility import MathUtils
from timer import Timer

class Brain:
    """The brain: parses lines, combines data classes to make decisions"""
    def __init__(self, bot):
        with Timer() as t:
            self.bot = bot
            self.load_realtime_data()
            self.load_precalc_data()
            self.iterations = 2000
        self.bot.log("Brain started up in {t} secs".format(t=t.secs))

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

    def do_turn(self, timeLeft_ms):
        """Wraps internal __do_turn so we can time how long each turn takes"""
        with Timer() as t:
            self.__do_turn(timeLeft_ms)
        self.bot.log("Finished turn in {t}s ({i} sims), had {l}s remaining"
                     .format(t=t.secs, i=self.iterations,
                             l=(timeLeft_ms/1000 - t.secs)))

    def __do_turn(self, timeLeft_ms):
        """Callback for when the brain has to make a decision"""
        if not self.data.hand:
            self.bot.log("No hand, killing ourselves. Data={d}".format(d=self.data))
            self.bot.fold()
            return

        hand = self.data.hand
        pot_odds = self.pot_odds()
        equity = 0

        if not self.data.table_cards:
            equity = self.preflop_equity[repr(hand)]
        else:
            simulator = HandSimulator(hand, self.data.table_cards)
            best_hand, score = simulator.best_hand()
            self.bot.log("best 5: {b} score: {s}" \
                         .format(b=str(best_hand), s=score))
            equity = simulator.simulate(self.iterations)

        self.bot.log("{h}, equity: {e}%, pot odds: {p}%" \
          .format(h=hand, e=equity, p=pot_odds))

        self.pick_action(equity, pot_odds)

    def pick_action(self, equity, pot_odds):
        """Look at our expected return and do something.
        Will be a semi-random mix of betting, folding, calling"""
        to_call = self.data.sidepot
        # action to us: check or bet
        if to_call == 0:
            if equity > 0.7 or self.r_test(0.03):
                self.bot.bet(self.big_raise())
            elif equity > 0.5 or self.r_test(0.05):
                self.bot.minimum_bet()
            else: # equity <= 0.3:
                self.bot.check()

        # use pot odds to call/bet/fold
        else:
            return_ratio = equity / pot_odds
            if return_ratio > 1.5 or self.r_test(0.02):
                self.bot.bet(self.big_raise())
            elif return_ratio > 1:
                self.bot.call(to_call)
            else:
                self.bot.fold()

    def big_raise(self):
        """Returns a big raise, 30-50% of the pot"""
        pot = self.data.pot
        bet_raise = random.uniform(0.3, 0.5) * pot
        self.bot.log("big raise of {r}".format(r=bet_raise))
        return bet_raise

    def minimum_bet(self):
        """Returns a minimum bet, 2.5 BB"""
        bet = 2.5 * self.data.big_blind
        self.bot.log("min bet of {b}".format(b=bet))
        return bet

    def r_test(self, fraction):
        """Given a number [0,1], randomly return true / false
        s.t. r_test(0.5) is true ~50% of the time"""
        passed = random.uniform(0,1) < fraction
        if passed:
            self.bot.log("r_test() passed for %{f}".format(f=fraction))
        return passed
