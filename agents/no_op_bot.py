#!/usr/bin/python
import sys
from check_fold_bot import CheckBrain, CheckFoldBot


class NoOpBrain(CheckBrain):
    def do_turn(self, bot, time_left_ms):
        pass


class NoOpBot(CheckFoldBot):
    """Dummy poker bot that never does anything"""
    def add_brain(self):
        self.brain = NoOpBrain(self)

if __name__ == '__main__':
    bot = NoOpBot(sys.stdin, sys.stdout, sys.stderr)
    bot.run()
