import sys
from brain import Brain

class TheAiGameBot(object):
    """ Bot for TheAiGame.com """
    def __init__(self, output, error):
        self.brain = Brain(self)
        self.output = output
        self.error = error

    def run(self):
        """ Main run loop """
        while not sys.stdin.closed:
            try:
                rawline = sys.stdin.readline()
                if len(rawline) == 0:
                    break
                line = rawline.strip()
                self.brain.parse_line(line)
            except EOFError:
                return

    def write_out(self, line):
        """Writes a line to the output"""
        self.write_line(line, self.output)

    def log(self, line):
        """Writes a line to the error"""
        self.write_line(line, self.error)

    def write_line(self, line, dest):
        if line and dest:
            dest.write(line)
            dest.flush()

if __name__ == '__main__':
    bot = TheAiGameBot(sys.stdout, sys.stderr)
    bot.run()
