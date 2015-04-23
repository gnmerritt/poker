#!/usr/bin/python
import sys
from check_fold_bot import CheckBrain, CheckFoldBot


class CallBrain(CheckBrain):
    def do_turn(self, bot, time_left_ms):
        self.bot.call(0) # adjusted to the correct amount by the game engine


class CallBot(CheckFoldBot):
    """Dummy poker bot that always calls"""
    def add_brain(self):
        self.brain = CallBrain(self)

if __name__ == '__main__':
    bot = CallBot(sys.stdin, sys.stdout, sys.stderr)
    bot.run()
