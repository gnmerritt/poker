#!/usr/bin/python
import sys
import random
from check_fold_bot import CheckBrain, CheckFoldBot


class CallRaiseBrain(CheckBrain):
    def do_turn(self, bot, time_left_ms):
        if random.uniform(0, 1) > 0.5:
            self.bot.bet(10)
        else:
            self.bot.call(0)


class CallRaiseBot(CheckFoldBot):
    """Dummy poker bot that splits raising or calling 50/50"""
    def add_brain(self):
        self.brain = CallRaiseBrain(self)

if __name__ == '__main__':
    bot = CallRaiseBot(sys.stdin, sys.stdout, sys.stderr)
    bot.run()
