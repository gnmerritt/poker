import sys
from brain import Brain
from theaigame import TheAiGameParserDelegate

class TheAiGameBot:
    """ Bot for TheAiGame.com """
    def __init__(self, output, error):
        self.brain = Brain(self, TheAiGameParserDelegate())
        self.output = output
        self.log = error

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

    def say(self, line):
        """Writes a line where the game controller can see it"""
        self.__write_line(line, self.output)

    def log(self, line):
        """Writes a line somewhere we can log it"""
        self.__write_line(line, self.log)

    def __write_line(self, line, dest):
        if line and dest:
            dest.write(line)
            dest.flush()

if __name__ == '__main__':
    bot = TheAiGameBot(sys.stdout, sys.stderr)
    bot.run()
