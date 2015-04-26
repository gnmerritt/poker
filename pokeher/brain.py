from __future__ import division
import cPickle as pickle

import cython_random as random
import utility
from game import GameData
from hand_simulator import HandSimulator
from timer import Timer


class Brain(object):
    """The brain: parses lines, combines data classes to make decisions"""
    def __init__(self, bot):
        with Timer() as t:
            self.bot = bot
            self.load_realtime_data()
            self.load_precalc_data()
            self.iterations = 400
        self.bot.log("Brain started up in {t} secs".format(t=t.secs))

    def load_realtime_data(self):
        sharedData = {}
        self.parser = self.bot.set_up_parser(sharedData, self.do_turn)
        self.data = GameData(sharedData)
        self.data.reset()

    def load_precalc_data(self):
        """Loads pre-computed hand data"""
        infile = utility.get_data_file('preflop_wins_50000.pickle')
        try:
            in_stream = open(infile, 'r')
            try:
                self.preflop_equity = pickle.load(in_stream)
                self.bot.log("Loaded preflop equity file")
            finally:
                in_stream.close()
        except IOError as e:
            self.bot.log("IO error loading {f} (e={e})" \
                         .format(f=infile, e=e))

    def parse_line(self, line):
        """Feeds a line to the parsers"""
        success = self.parser.handle_line(line)
        if success:
            self.data.update()
        else:
            self.bot.log("didn't handle line: '{}'".format(line))

    def to_call(self, silent=False):
        to_call = self.data.to_call
        if not silent:
            self.bot.log("bot={}, pot={}, to call={}" \
                         .format(self.data.me, self.data.pot, to_call))
        return to_call

    def pot_odds(self):
        """Return the pot odds, or how much we need to gain to call"""
        to_call = self.to_call()
        return utility.MathUtils.percentage(to_call, self.data.pot + to_call)

    def do_turn(self, bot, time_left_ms):
        """Wraps internal __do_turn so we can time how long each turn takes"""
        if not bot or bot != self.data.me:
            return
        with Timer() as t:
            self.__do_turn(time_left_ms)
        if not self.data.table_cards:
            turn_type = "preflop"
        else:
            turn_type = "{} sims".format(self.iterations)
        self.bot.log("Finished turn in {t}s ({s}), had {l}s remaining"
                     .format(t=t.secs, s=turn_type,
                             l=(time_left_ms/1000 - t.secs)))

    def __do_turn(self, time_left_ms):
        """Callback for when the brain has to make a decision"""
        if not self.data.hand:
            self.bot.log("No hand, killing ourselves. Data={d}"
                         .format(d=self.data))
            self.bot.fold()
            return

        hand = self.data.hand
        pot_odds = self.pot_odds()
        equity = 0

        if not self.data.table_cards:
            equity = self.preflop_equity[repr(hand)]
            source = "preflop"
        else:
            simulator = HandSimulator(hand, self.data.table_cards)
            best_hand, score = simulator.best_hand()
            self.bot.log(" best 5: {b} score: {s}"
                         .format(b=[str(c) for c in best_hand], s=score))
            equity = simulator.simulate(self.iterations)
            source = "sim"

        self.bot.log(" {h}, win: {e}% ({s}), pot odds: {p}%"
                     .format(h=hand, e=equity, s=source, p=pot_odds))

        self.pick_action(equity, pot_odds)

    def pick_action(self, equity, pot_odds):
        """Look at our expected return and do something.
        Will be a semi-random mix of betting, folding, calling"""
        to_call = self.to_call(silent=True)

        # action to us: check or bet
        if to_call == 0:
            if equity > 65 or (equity > 40 and self.r_test(0.03, 'c1')):
                self.bot.bet(self.big_raise("R1"))
            elif equity > 55 or self.r_test(0.02, 'c2'):
                self.minimum_bet()
            else:
                self.bot.check()
        # use pot odds to call/bet/fold
        else:
            return_ratio = equity / pot_odds
            self.bot.log(" return ratio={}".format(return_ratio))
            if equity > 70 or (equity > 40 and self.r_test(0.03, 'po1')):
                self.bot.bet(self.big_raise("R2"))
            elif return_ratio > 1:
                self.bot.call(to_call)
            else:
                self.bot.fold()

    def big_raise(self, source=None):
        """Returns a big raise, 70-150% of the pot"""
        pot = self.data.pot
        bet_raise = random.uniform(0.7, 1.5) * pot
        self.bot.log(" big raise of {r} (pot={p}) from {s}"
                     .format(r=bet_raise, p=pot, s=source))
        return self.__round_bet(bet_raise)

    def __round_bet(self, val):
        if val is not None:
            return int(round(val))

    def minimum_bet(self):
        """Returns a minimum bet, 2.5-4 BB"""
        bet = self.data.big_blind * random.uniform(2, 4)
        self.bot.log("min bet of {b}".format(b=bet))
        return self.__round_bet(bet)

    def r_test(self, fraction, block=None):
        """Given a number [0,1], randomly return true / false
        s.t. r_test(0.5) is true ~50% of the time"""
        passed = random.uniform(0, 1) < fraction
        if passed:
            self.bot.log(" r_test({f}%) passed from {b}"
                         .format(f=100*fraction, b=block))
        return passed
