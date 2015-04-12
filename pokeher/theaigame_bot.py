#!/usr/bin/python

import sys
sys.path.append('/Users/nathan/sources/poker/') ## TODO fix
try:
    from wiring import IOPokerBot
except ImportError as e:
    import os, platform
    print "Couldn't load bot on os={os}, sys={s}, rel={r}, e={e}" \
      .format(os=os.name, s=platform.system(), r=platform.release(), e=e)
    sys.exit()
from theaigame import TheAiGameParserDelegate, TheAiGameActionDelegate


class TheAiGameBot(IOPokerBot,
                   TheAiGameParserDelegate, TheAiGameActionDelegate):
    """Poker bot for TheAiGame.com"""
    pass

if __name__ == '__main__':
    bot = TheAiGameBot(sys.stdin, sys.stdout, sys.stderr)
    bot.run()
