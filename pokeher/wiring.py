from brain import Brain

class IOPokerBot(object):
    """Generic Poker Bot, can read & write lines.
    Subclasses should mix-in parser & action delegates
    """
    def __init__(self, io_input, io_output, log_output):
        self.io_input = io_input
        self.action_out = io_output
        self.log_out = log_output
        self.brain = Brain(self)

    def run(self):
        """ Main run loop """
        while not self.io_input.closed:
            try:
                rawline = self.io_input.readline()
                if len(rawline) == 0:
                    break
                line = rawline.strip()
                self.brain.parse_line(line)
            except EOFError:
                return

    def say(self, line):
        """Writes a line where the game controller can see it"""
        self.write_line(line, self.action_out)
        self.log("SAID :: {l}".format(l=line))

    def log(self, line):
        """Writes a line somewhere we can log it"""
        self.write_line(line, self.log)

    def write_line(self, line, dest):
        if line and dest:
            dest.write(line)
            dest.write('\n')
            dest.flush()

class BufferPokerBot(IOPokerBot):
    """Reads to and writes from lists of strings for easier testing """
    def write_line(self, line, dest):
        if line and dest is not None:
            dest.append(line)

    def run(self):
        for line in self.io_input:
            self.brain.parse_line(line)

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
