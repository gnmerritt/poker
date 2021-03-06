from __future__ import print_function
import time

from twisted.internet import reactor

from bots import LoadedBot
from arena import PyArena


class LocalIOArena(PyArena):
    """Loads Python bots from source folders, sets up IO channels to them"""
    def __init__(self, delay_secs=1, silent=False):
        PyArena.__init__(self, silent)
        self.delay_secs = delay_secs
        self.print_bot_output = True

    def log_func(self, message, end=""):
        print(message, end)

    def load_bot(self, source_file):
        """Starts a bot as a subprocess, given its path"""
        seat = self.bot_count()
        self.log("loading bot {l} from {f}".format(l=seat, f=source_file))
        bot = LoadedBot(source_file, seat, print_bot_output=self.print_bot_output)
        if bot and not bot.process.exploded:
            self.bots.append(bot)

    def run(self, args):
        for file in args:
            self.load_bot(file)
        if self.min_players() <= self.bot_count() <= self.max_players:
            self.log("Have enough bots, starting match in {}s"
                     .format(self.delay_secs))
            time.sleep(self.delay_secs)
            return self.play_match()
        else:
            self.log("Wrong # of bots ({i}) needed {k}-{j}. Can't play"
                     .format(i=self.bot_count(), k=self.min_players(),
                             j=self.max_players()))

    def get_action(self, bot_name, got_action):
        """Tells a bot to go, waits for a response"""
        self.notify_bots_turn(bot_name)
        bot = self.bot_from_name(bot_name)
        timebank = self.get_time_for_move(bot_name)
        answer = bot.ask(timebank)
        if not answer:
            return None
        time, response = answer
        #  TODO: hook time taken back in to bot state
        self.log("bot {b} submitted action {a} chips={c} in {t}s"
                 .format(b=bot_name, a=response, c=bot.state.stack, t=time))
        action = self.get_parsed_action(response)
        reactor.callLater(0.001, got_action.callback, action)

    def skipped(self, bot_name, deferred):
        reactor.callLater(0.001, deferred.callback, "")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for bot in self.bots:
            bot.kill()
