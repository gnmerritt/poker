import time


class IOPokerBot(object):
    """Generic Poker Bot, can read & write lines.
    Subclasses should mix-in parser & action delegates
    """
    def __init__(self, io_input, io_output, log_output):
        self.no_logging = False
        self.io_input = io_input
        self.action_out = io_output
        self.log_out = log_output
        self.add_brain()

    def add_brain(self):
        """Overridden by subclasses to make this bot go"""
        pass

    def run(self):
        """ Main run loop """
        while True:
            try:
                rawline = self.io_input.readline()
                if len(rawline) == 0:
                    time.sleep(0.001) # sleep for 1ms
                    continue
                line = rawline.strip()
                self.brain.parse_line(line)
            except Exception as e:
                self.log("main loop exception of type '{}' msg='{}', args='{}'"
                         .format(type(e).__name__, e.message, e.args))
                if self.brain:
                    self.brain.bot.check()

    def say(self, line):
        """Writes a line where the game controller can see it"""
        self.write_line(line, self.action_out)
        self.log("SAID :: {l}".format(l=line))

    def log(self, line):
        """Writes a line somewhere we can log it"""
        if not self.no_logging:
            self.write_line(line, self.log_out)

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

    def handle_line(self, line):
        pass


class GameParserDelegate(object):
    """Generic parser delegate - passes lines to workers"""
    def handle_line(self, line):
        """Delegates the line to each worker"""
        for worker in self.workers:
            if worker.handle_line(line):
                return True
        return False
