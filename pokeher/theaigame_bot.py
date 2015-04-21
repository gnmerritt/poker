#!/usr/bin/python
from __future__ import print_function
import sys

try:
    import utility
    utility.fix_paths()
    from wiring import IOPokerBot
except ImportError as e:
    import platform, os
    error = "Couldn't load bot on os={os}, sys={s}, rel={r}, e={e}" \
          .format(os=os.name, s=platform.system(), r=platform.release(), e=e)
    print(error, file=sys.stderr)
    sys.exit()

from theaigame import TheAiGameParserDelegate, TheAiGameActionDelegate


class TheAiGameBot(IOPokerBot,
                   TheAiGameParserDelegate, TheAiGameActionDelegate):
    """Poker bot for TheAiGame.com"""
    pass

if __name__ == '__main__':
    bot = TheAiGameBot(sys.stdin, sys.stdout, sys.stderr)
    bot.run()
