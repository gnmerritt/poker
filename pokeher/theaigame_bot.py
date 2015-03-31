#!/usr/bin/python

import sys
sys.path.append('/Users/nathan/sources/poker/') ## TODO fix
from wiring import IOPokerBot
from theaigame import TheAiGameParserDelegate, TheAiGameActionDelegate


class TheAiGameBot(IOPokerBot,
                   TheAiGameParserDelegate, TheAiGameActionDelegate):
    """Poker bot for TheAiGame.com"""
    pass

if __name__ == '__main__':
    bot = TheAiGameBot(sys.stdin, sys.stdout, sys.stderr)
    bot.run()
