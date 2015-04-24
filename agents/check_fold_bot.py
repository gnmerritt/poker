#!/usr/bin/python
import sys
import utility
utility.fix_paths()
from pokeher.wiring import IOPokerBot
from pokeher.theaigame import TheAiGameParserDelegate, TheAiGameActionDelegate


class CheckBrain(object):
    def __init__(self, bot):
        self.bot = bot
        self.bot.no_logging = True
        self.parser = self.bot.set_up_parser({}, self.do_turn)

    def parse_line(self, line):
        self.parser.handle_line(line)

    def do_turn(self, bot, time_left_ms):
        self.bot.check()


class CheckFoldBot(IOPokerBot,
                   TheAiGameParserDelegate, TheAiGameActionDelegate):
    """Dummy poker bot that only checks"""
    def add_brain(self):
        self.brain = CheckBrain(self)

if __name__ == '__main__':
    bot = CheckFoldBot(sys.stdin, sys.stdout, sys.stderr)
    bot.run()
