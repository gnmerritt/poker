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
        self.action_callback = None
        self.started_waiting = None

    def add_bot(self, bot_key, connection, name=None):
        if bot_key in self.bot_keys:
            return
        self.bot_keys[bot_key] = True

        seat = len(self.bots)
        bot = NetLoadedBot(bot_key, seat)
        bot.bind_connection(connection)
        self.bots.append(bot)

        if len(self.bots) >= self.min_players() and not self.playing:
            self.playing = True
            self.start_match()

    def start_match(self):
        def on_match_complete(args):
            twisted_log.msg("** match completed **")

        twisted_log.msg("** starting match! **")
        on_complete, play_fn = self.play_match()
        on_complete.addBoth(on_match_complete)
        play_fn()

    def get_action(self, bot_name, callback):
        """Async version of get_action that waits on net input"""
        self.notify_bots_turn(bot_name)
        self.waiting_on = bot_name
        self.action_callback = callback
        self.started_waiting = time.clock()

        twisted_log.msg("RUNNING ASYNC GET_ACTION")
        # TODO: timeouts, clock time per bot

    def bot_said(self, bot, line):
        if line.startswith("!"):
            twisted_log.msg("ignoring server command line: {}".format(line))
            return
        if bot != self.waiting_on:
            twisted_log.msg("ignoring input from {}".format(bot))
            return
        if not line:
            twisted_log.msg("ignoring empty line from {}".format(bot))
            return

        twisted_log.msg("GOT VALID LINE FROM BOT: \n  {}".format(line))

        self.waiting_on = None
        if self.action_callback:
            delay = time.clock() - self.started_waiting
            twisted_log.msg("got response in {}s".format(delay))
            self.action_callback(self.get_parsed_action(line))

    def log(self, message, force=False):
        twisted_log.msg(message)

    def silent_update(self, message):
        pass


class TwistedNLHEArena(NetworkArena, Holdem, NoBetLimit, FiveSecondTurns):
    """No limit Texas hold'em game via the internet"""
    pass
