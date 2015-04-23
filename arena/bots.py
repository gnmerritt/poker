import sys
import types
import subprocess as sp
from threading  import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

from pokeher.timer import Timer

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()


class BotProcess(object):
    def __init__(self, source_file):
        self.exploded = False
        self.process = self.process_out = None
        try:
            self.process = p = sp.Popen([source_file],
                                        stdin=sp.PIPE,
                                        stdout=sp.PIPE,
            #stderr=sp.PIPE,
                                        bufsize=1,
                                        close_fds=ON_POSIX)
            self.process_out = Queue()
            t = Thread(target=enqueue_output, args=(p.stdout, self.process_out))
            t.daemon = True # thread dies with the program
            t.start()
        except OSError as e:
            print "bot file doesn't exist, skipping {}".format(repr(e))
            self.exploded = True
        # TODO: more error catching probably

    def put(self, line):
        if self.process:
            self.process.stdin.write(line)
            self.process.stdin.write('\n')
            self.process.stdin.flush()

    def get(self, timeout=0.5):
        """Gets the most recent line
        """
        line = None
        with Timer() as t:
            try:
                line = self.process_out.get(timeout=timeout)
            except Empty:
                pass
        return t.secs, line

    def shutdown(self):
        if self.process:
            self.process.kill()


class BotState(object):
    INITIAL_CHIPS = 1000 # TODO

    """Stuff to remember about each bot"""
    def __init__(self, seat, source_file):
        self.source = source_file
        self.name = 'bot_{s}'.format(s=seat)  # name for communication
        self.seat = seat  # seat at table
        self.stack = self.INITIAL_CHIPS # amount of chips
        self.stake = 0  # chips bet currently


class LoadedBot(object):
    """Holds an instance of each bot, keeps track of game info about it"""
    def __init__(self, source_file, seat):
        self.process = BotProcess(source_file)
        self.state = BotState(seat, source_file)
        self.is_active = True

    def tell(self, line):
        """Writes to the bot's STDIN"""
        assert type(line) is types.StringType, \
          "can't tell non-string '{}'".format(line)
        self.process.put(line)

    def ask(self):
        return self.process.get()

    def change_chips(self, delta):
        self.state.stack += delta

    def name(self):
        return self.state.name

    def chips(self):
        if not self.is_active:
            return 0
        return self.state.stack

    def kill(self):
        """Kills the bot"""
        self.is_active = False
        self.process.shutdown()
