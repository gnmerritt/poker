import time
from twisted.python import log as twisted_log

import utility
utility.fix_paths()

from holdem import Holdem
from arena import PyArena
from betting import NoBetLimit
from bots import NetLoadedBot
from timing import FiveSecondTurns


class NetworkArena(PyArena):
    def __init__(self):
        PyArena.__init__(self)
        self.playing = False
        self.bot_keys = {}

        self.waiting_on = None
        self.action_deferred = None
        self.started_waiting = None

    def add_bot(self, bot_key, connection, name=None):
        if bot_key in self.bot_keys:
            return

        seat = len(self.bots)
        bot = NetLoadedBot(bot_key, seat)
        self.bot_keys[bot_key] = bot.name()
        bot.bind_connection(connection)
        self.bots.append(bot)

        if len(self.bots) >= self.min_players() and not self.playing:
            self.playing = True
            self.start_match()

    def start_match(self):
        def on_match_complete(args):
            self.log("** match completed **")

        self.log("** starting match! **")
        on_complete, play_fn = self.play_match()
        on_complete.addBoth(on_match_complete)
        play_fn()

    def get_action(self, bot_name, deferred):
        """Async version of get_action that waits on net input"""
        self.notify_bots_turn(bot_name)
        self.waiting_on = bot_name
        self.action_deferred = deferred
        self.started_waiting = time.clock()

        # TODO: timeouts, clock time per bot

    def bot_said(self, bot_name, line):
        bot = self.bot_keys.get(bot_name, None)
        if line.startswith("!"):
            self.log("ignoring server command line: {}".format(line))
            return
        if not bot or bot != self.waiting_on:
            self.log("ignoring input from {}".format(bot))
            return
        if not line:
            self.log("ignoring empty line from {}".format(bot))
            return

        self.waiting_on = None
        if self.action_deferred:
            delay = time.clock() - self.started_waiting
            self.log("got response in {}s".format(delay))
            self.action_deferred.callback(self.get_parsed_action(line))

    def skipped(self, bot_name, deferred):
        deferred.callback("")

    def log(self, message, force=False):
        twisted_log.msg(message)

    def silent_update(self, message):
        pass


class TwistedNLHEArena(NetworkArena, Holdem, NoBetLimit, FiveSecondTurns):
    """No limit Texas hold'em game via the internet"""
    pass
