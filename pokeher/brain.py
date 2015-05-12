from __future__ import division

import time

import cython_random as random
import preflop_equity
from utility import MathUtils
from game import GameData
from hand_simulator import HandSimulator
from bet_sizing import BetSizeCalculator
from fear import Fear
from timer import Timer


class Brain(BetSizeCalculator, Fear):
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
        preflop = preflop_equity.PreflopEquity(log_func=self.bot.log)
        self.preflop_equity = preflop.data

    def parse_line(self, line):
        """Feeds a line to the parsers"""
        success = self.parser.handle_line(line)
        if success:
            self.data.update()
        else:
            self.bot.log("didn't handle line: '{}'".format(line))

    def do_turn(self, bot, total_time_left_ms):
        """Wraps internal __do_turn so we can time how long each turn takes"""
        time_left = min(total_time_left_ms, self.data.time_per_move)
        if not bot or bot != self.data.me:
            return
        with Timer() as t:
            self.__do_turn(time_left)
        if not self.data.table_cards:
            turn_type = "preflop"
        else:
            turn_type = "{} sims".format(self.iterations)
        left = (time_left / 1000) - t.secs
        self.bot.log("Finished turn in {t}s ({s}), had {l}s remaining"
                     .format(t=t.secs, s=turn_type, l=left))

    def __do_turn(self, time_left_ms):
        """Callback for when the brain has to make a decision"""
        if not self.data.hand:
            self.bot.log("No hand, killing ourselves. Data={d}"
                         .format(d=self.data))
            self.bot.fold()
            return

        hand = self.data.hand
        stack = self.our_stack()
        to_call = self.to_call(silent=False)
        pot_odds = self.pot_odds()
        equity = 0
        self.update_fear(to_call)
        preflop_fear = self.data.preflop_fear
        hand_fear = self.data.hand_fear

        # preflop, no big raises. safe to use our precalculated win %
        if not self.data.table_cards and preflop_fear == -1:
            equity = self.preflop_equity[hand.simple()]
            source = "preflop"
        else:
            simulator = HandSimulator(hand, self.data.table_cards,
                                      self.preflop_equity)
            best_hand, score = simulator.best_hand()
            equity = self.__run_simulator(simulator, time_left_ms,
                                          preflop_fear, hand_fear)
            source = "sim"

        self.bot.log(" hand: {h}, table: {t}"
                     .format(h=hand, t=[str(t) for t in self.data.table_cards]))
        if self.data.table_cards:
            self.bot.log(" best 5: {b} score: {s}"
                         .format(b=[str(c) for c in best_hand], s=str(score)))
        self.bot.log(" win: {e:.2f}% ({s}), pot odds: {p:.2f}%, stack={m}"
                     .format(e=equity, s=source, p=pot_odds, m=stack))
        self.bot.log(" pre-fear={pf}, hand-fear=({hf})"
                     .format(pf=preflop_fear, hf=hand_fear))

        self.pick_action(equity, to_call, pot_odds)

    def __run_simulator(self, simulator, time_left_ms, hand_filter, hand_fear):
        results = []
        step_size = 100
        start_time = time.clock() * 1000
        end_time = start_time + time_left_ms - 50
        for i in range(0, self.iterations, step_size):
            now = time.clock() * 1000
            if now >= end_time:
                self.bot.log(" stopping simulation after {} runs".format(i))
                break
            equity = simulator.simulate(step_size, hand_filter, hand_fear)
            results.append(equity)
        return sum(results) / len(results)

    def pick_action(self, equity, to_call, pot_odds):
        """Look at our expected return and do something.
        Will be a semi-random mix of betting, folding, calling"""
        # action to us: check or bet
        if to_call == 0:
            # lock hands - 1/3 of the time make a small bet instead of a big one
            if equity > 90 and self.r_test(0.33, 'lock_trap'):
                self.make_bet(self.minimum_bet("trap1"))
            elif equity > 65 or (equity > 40 and self.r_test(0.03, 'c1')):
                self.make_bet(self.big_raise("R1"))
            elif equity > 55 or self.r_test(0.02, 'c2'):
                self.make_bet(self.minimum_bet("R2"))
            else:
                self.bot.check()
        # TODO: combine these and make them aware of button
        # use pot odds to call/bet/fold
        else:
            return_ratio = equity / pot_odds
            self.bot.log(" return ratio={:.3f}".format(return_ratio))
            if equity > 70 or (equity > 40 and self.r_test(0.03, 'po1')):
                self.make_bet(self.big_raise("R3"))
            elif to_call < self.data.big_blind and \
               (equity > 55 or self.r_test(0.03, 'po2')):
                # small preflop raise from SB, get more money into the pot
                self.make_bet(self.minimum_bet("R4"))
            elif return_ratio > 1.25:
                self.bot.log(" return ratio > 1.25, calling {}".format(to_call))
                self.bot.call(to_call)
            elif return_ratio > 1 \
              and MathUtils.percentage(to_call, self.our_stack()) < 10:
                self.bot.log(" return ratio > 1 and bet is small, calling {}"
                             .format(to_call))
                self.bot.call(to_call)
            else:
                self.bot.fold()

    def make_bet(self, amount):
        """Make a bet, also update fear assumming the opponent will call."""
        self.update_fear(amount)
        self.bot.bet(amount)

    def r_test(self, fraction, block=None):
        """Given a number [0,1], randomly return true / false
        s.t. r_test(0.5) is true ~50% of the time"""
        passed = random.uniform(0, 1) < fraction
        if passed:
            self.bot.log(" r_test({f}%) passed from {b}"
                         .format(f=100*fraction, b=block))
        return passed
