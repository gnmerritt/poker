import sys
from wiring import IOPokerBot
from theaigame import TheAiGameParserDelegate, TheAiGameActionDelegate

class TheAiGameBot(IOPokerBot, TheAiGameParserDelegate, TheAiGameActionDelegate):
    """The poker bot for TheAiGame.com"""
    pass

if __name__ == '__main__':
    bot = TheAiGameBot(sys.stdout, sys.stderr)
    bot.run()
