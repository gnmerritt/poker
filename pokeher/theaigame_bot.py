import sys
from wiring import IOPokerBot
from brain import Brain
from theaigame import TheAiGameParserDelegate

class TheAiGameBot(IOPokerBot):
    """ Bot for TheAiGame.com """
    def __init__(self, output, error):
        super(TheAiGameBot, self).__init__(output, error)
        self.brain = Brain(self, TheAiGameParserDelegate())

if __name__ == '__main__':
    bot = TheAiGameBot(sys.stdout, sys.stderr)
    bot.run()
