from twisted.python import log as twisted_log

import utility
utility.fix_paths()

from holdem import Holdem
from arena import PyArena
from betting import NoBetLimit
from bots import NetLoadedBot
from timing import FiveSecondTurns


class NetworkArena(object):
    def __init__(self):
        self.playing = False
        self.bot_keys = {}
        self.common_setup()

    def add_bot(self, bot_key, connection, name=None):
        if bot_key in self.bot_keys:
            twisted_log.msg("duplicate key, bailing")
            return
        twisted_log.msg("got new bot, adding")
        self.bot_keys[bot_key] = True

        seat = len(self.bots) + 1
        twisted_log.msg("new bot at seat {}".format(seat))

        bot = NetLoadedBot(bot_key, seat)
        bot.bind_connection(connection)
        self.bots.append(bot)

        if len(self.bots) >= self.min_players() and not self.playing:
            twisted_log.msg("** starting match! **")
            self.play_match()

    def log(self, message, force=False):
        twisted_log.msg(message)

    def silent_update(self, message):
        pass


class TwistedNLHEArena(NetworkArena, PyArena, Holdem, NoBetLimit, FiveSecondTurns):
    """No limit Texas hold'em game via the internet"""
    pass
