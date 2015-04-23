#!/usr/bin/python
import sys
from check_fold_bot import CheckBrain, CheckFoldBot


class RaiseBrain(CheckBrain):
    def do_turn(self, bot, time_left_ms):
        self.bot.bet(10)


class RaiseBot(CheckFoldBot):
    """Dummy poker bot that always raises the minimum"""
    def add_brain(self):
        self.brain = RaiseBrain(self)

if __name__ == '__main__':
    bot = RaiseBot(sys.stdin, sys.stdout, sys.stderr)
    bot.run()
