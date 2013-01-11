import sys
from theaigame import *

class TheAiGameBot(object):
    """ Bot for TheAiGame.com """
    def __init__(self, output, error):
        self.output = output
        self.error = error
        sharedData = {}
        self.parsers = [ SettingsParser(sharedData),
                         RoundParser(sharedData),
                         TurnParser(sharedData, self.do_turn) ]

    def do_turn(self, timeLeft):
        """Callback for when the bot has to make a decision"""
        self.write_out('call 0')

    def run(self):
        """ Main run loop """
        while not sys.stdin.closed:
            try:
                rawline = sys.stdin.readline()
                if len(rawline) == 0:
                    break
                line = rawline.strip()
                self.parse_line(line)
            except EOFError:
                return

    def parse_line(self, line):
        """Feeds a line to the parsers"""
        for parser in self.parsers:
            if parser.handle_line(line):
                return
        self.write_error("didn't handle line: " + line)

    def write_out(self, line):
        """Writes a line to the output"""
        self.write_line(line, self.output)

    def write_error(self, line):
        """Writes a line to the error"""
        self.write_line(line, self.error)

    def write_line(self, line, dest):
        if line and dest:
            dest.write(line)
            dest.flush()

# Following comment needed to make the bot run:
#  __poker_main__
if __name__ == '__main__':
    bot = TheAiGameBot(sys.stdout, sys.stderr)
    bot.run()
