class IOPokerBot(object):
    """Generic Poker Bot, can read & write lines.
    Subclasses should define a brain for the bot to use"""
    def __init__(self, output, error):
        self.output = output
        self.log = error
        self.brain = None

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

class Parser(object):
    """Parsers handle lines and store data into self.data"""
    def __init__(self, data):
        self._data = data

    def handle_line(self,line):
        pass

class GameParserDelegate(object):
    """Generic parser delegate - passes lines to workers"""
    def handle_line(self, line):
        """Delegates the line to each worker"""
        for worker in self.workers:
            if worker.handle_line(line):
                return True
        return False

    def set_up(self, data, turn_callback):
        pass
