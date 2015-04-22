from __future__ import division
import cPickle as pickle
try:
    import random
except:
    import fake_random as random

import utility
from game import GameData
from hand_simulator import HandSimulator
from timer import Timer


class Brain:
    """The brain: parses lines, combines data classes to make decisions"""
    def __init__(self, bot):
        with Timer() as t:
            self.bot = bot
            self.load_realtime_data()
            self.load_precalc_data()
            self.iterations = 1000
        self.bot.log("Brain started up in {t} secs".format(t=t.secs))

    def load_realtime_data(self):
        sharedData = {}
        self.parser = self.bot.set_up_parser(sharedData, self.do_turn)
        self.data = GameData(sharedData)
        self.data.reset()

    def load_precalc_data(self):
        """Loads pre-computed hand data"""
        infile = utility.get_data_file('preflop_wins_5000.pickle')
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

    def to_call(self):
        to_call = self.data.to_call
        self.bot.log("bot={}, pot={}, to call={}" \
                     .format(self.data.me, self.data.pot, to_call))
        return to_call

    def pot_odds(self):
        """Return the pot odds, or how much we need to gain to call"""
        to_call = self.to_call()
        return utility.MathUtils.percentage(to_call, self.data.pot)

    def do_turn(self, bot, timeLeft_ms):
        """Wraps internal __do_turn so we can time how long each turn takes"""
        if not bot or bot != self.data.me:
            return
        with Timer() as t:
            self.__do_turn(timeLeft_ms)
        self.bot.log("Finished turn in {t}s ({i} sims), had {l}s remaining"
                     .format(t=t.secs, i=self.iterations,
                             l=(timeLeft_ms/1000 - t.secs)))

    def __do_turn(self, timeLeft_ms):
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
        else:
            simulator = HandSimulator(hand, self.data.table_cards)
            best_hand, score = simulator.best_hand()
            self.bot.log("best 5: {b} score: {s}"
                         .format(b=[str(c) for c in best_hand], s=score))
            equity = simulator.simulate(self.iterations)

        self.bot.log("{h}, equity: {e}%, pot odds: {p}%"
                     .format(h=hand, e=equity, p=pot_odds))

        self.pick_action(equity, pot_odds)

    def pick_action(self, equity, pot_odds):
        """Look at our expected return and do something.
        Will be a semi-random mix of betting, folding, calling"""
        to_call = self.to_call()

        # action to us: check or bet
        if to_call == 0:
            if equity > 0.8 or self.r_test(0.03):
                self.bot.bet(self.big_raise())
            elif equity > 0.6 or self.r_test(0.05):
                self.bot.minimum_bet()
            else:  # equity <= 0.3:
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
        self.bot.log("big raise of {r} (pot={p})".format(r=bet_raise, p=pot))
        return self.__round_bet(bet_raise)

    def __round_bet(self, val):
        if val is not None:
            return int(round(val))

    def minimum_bet(self):
        """Returns a minimum bet, 2.5-4 BB"""
        bet = self.data.big_blind * random.uniform(2, 4)
        self.bot.log("min bet of {b}".format(b=bet))
        return self.__round_bet(bet)

    def r_test(self, fraction):
        """Given a number [0,1], randomly return true / false
        s.t. r_test(0.5) is true ~50% of the time"""
        passed = random.uniform(0, 1) < fraction
        if passed:
            self.bot.log("r_test() passed for %{f}".format(f=fraction))
        return passed
