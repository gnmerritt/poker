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
    def __init__(self, source_file, print_bot_output=True):
        self.exploded = False
        self.process = self.process_out = None
        output = sys.stderr if print_bot_output else sp.PIPE
        try:
            self.process = p = sp.Popen([source_file],
                                        stdin=sp.PIPE,
                                        stdout=sp.PIPE,
                                        stderr=output,
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

    def get(self, timeout=1):
        """Gets the most recent line"""
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
    INITIAL_CHIPS = 1000  # TODO
    TIMEBANK = 5  # seconds

    """Stuff to remember about each bot"""
    def __init__(self, seat, source_file):
        self.source = source_file
        self.name = 'bot_{s}'.format(s=seat)  # name for communication
        self.seat = seat  # seat at table
        self.stack = self.INITIAL_CHIPS  # amount of chips
        self.stake = 0  # chips bet currently
        self.timebank = self.TIMEBANK
        self.timeouts = 0

    def __repr__(self):
        return "Bot<'{}'@'{}' stk={}>" \
            .format(self.name, self.source, self.stack)


class LoadedBot(object):
    """Holds an instance of each bot, keeps track of game info about it"""
    def __init__(self, source_file, seat, print_bot_output=True):
        self.state = BotState(seat, source_file)
        self.is_active = True
        self.silent = not print_bot_output
        self.start_bot(source_file, print_bot_output)

    def start_bot(self, source_file, print_bot_output):
        self.process = BotProcess(
            source_file, print_bot_output=print_bot_output
        )

    def tell(self, line):
        """Writes to the bot's STDIN"""
        assert type(line) is types.StringType, \
            "can't tell non-string '{}'".format(line)
        try:
            self.process.put(line)
        except IOError as e:
            if not self.silent:
                print "Error talking to bot {}: {}" \
                    .format(self.state.source, e)

    def ask(self, timeout=1):
        return self.process.get(timeout)

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

    def __repr__(self):
        return repr(self.state)


class NetLoadedBot(LoadedBot):
    def start_bot(self, source_file, print_bot_output):
        pass

    def bind_connection(self, protocol):
        self.protocol = protocol

    def tell(self, line):
        self.protocol.sendLine(line)

    def ask(self):
        pass  # no-op, we let bots write back to us

    def kill(self, message="Match is over (killed)"):
        self.is_active = False
        self.protocol.closeBecause(message)
