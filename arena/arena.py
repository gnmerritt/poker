from __future__ import print_function

from twisted.internet import defer

import math
import os
import errno

import pokeher.cards as cards
from pokeher.theaigame import TheAiGameActionBuilder
from hand_stats import HandStats


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class PyArena(object):
    """Manages game state, communication, bot money
    Leaves I/O to subclasses
    """
    TIME_PER_MOVE = 2  # seconds
    ALLOWED_TIMEOUTS = 3

    def __init__(self, silent=False):
        self.silent = silent
        self.bots = []  # [LoadedBot or similar]
        self.stats = HandStats()
        self.output_directory = False
        self.key = False

    def log(self, message, force=False):
        if not self.silent or force:
            self.log_func(message)

    def silent_update(self, message):
        if self.silent:
            self.log_func(message, end="")

    def log_func(self, message, end):
        pass

    def bot_count(self):
        """Returns the current number of loaded bots"""
        return len(self.bots)

    def living_bots(self):
        """Returns bots that still have money"""
        return [b for b in self.bots if b.is_active]

    def living_bot_names(self):
        """Returns the names of living bots"""
        alive = self.living_bots()
        return [b.state.name for b in alive]

    def bot_stacks(self):
        """Returns a dict of bot_name => chips"""
        return {b.state.name: b.chips()
                for b in self.living_bots()}

    def bot_from_name(self, name):
        """Returns the bot with the given name"""
        for bot in self.bots:
            if bot.state.name == name:
                return bot
        return None

    def play_match(self):
        """Plays rounds of poker until all players are eliminated except one
        Uses methods from the games mixin, explodes otherwise"""
        self.init_game()
        self.say_match_updates()
        self.starting_money = sum(b.state.stack for b in self.living_bots())
        self.current_round = 0
        self.on_match_complete = defer.Deferred()
        return self.on_match_complete, self.__hand_tick

    def __hand_tick(self):
        """A tick of the arena will play one hand of poker, continuing
        until there is only one player remaining"""
        self.current_round += 1

        self.say_round_updates()
        if len(self.living_bots()) >= self.min_players():
            self.play_hand()
        else:
            self.declare_winners()
            self.on_match_complete.callback(MatchResults(self))

    def check_stack_sizes(self):
        self.log("after winnings, bot money:")
        for b in self.living_bots():
            self.log("  {} -> {}".format(b.state.name, b.state.stack))
        assert sum(b.state.stack for b in self.living_bots()) \
            == self.starting_money

    def declare_winners(self):
        winners = self.living_bots()
        lines = [
            "",
            "Match survivors: ",
        ]
        for b in winners:
            lines.append("  {c} chips : {n} ({f})".format(c=b.state.stack,
                                                          n=b.state.name,
                                                          f=b.state.source))
        lines.append("")
        lines.append(repr(self.stats))
        self.log("\n".join(lines))
        return winners

    def play_hand(self):
        """Plays a hand of poker, updating chip counts at the end."""
        def after_hand(args):
            winners, pot, log = args
            self.write_hand_log(log)
            self.__update_chips(winners, pot)
            self.__remove_dead_players()
            self.__hand_tick()

        hand = self.new_hand()
        on_hand_complete, start_func = hand.play_hand()
        on_hand_complete.addCallback(after_hand)
        start_func()

    def split_pot(self, pot, num_winners):
        prize_per_winner = pot / float(num_winners)
        prize_int = math.trunc(prize_per_winner)
        prizes = [prize_int] * num_winners
        if prize_per_winner != prize_int:
            # TODO: this only works in heads up
            # arbitrarily give the first player an extra chip :-)
            prizes[0] = prize_int + 1
        return prizes

    def __update_chips(self, winners, pot):
        num_winners = len(winners)
        winnings = self.split_pot(pot, num_winners)
        updates = []

        for i, name in enumerate(winners):
            prize = winnings[i]
            bot = self.bot_from_name(name)
            bot.change_chips(prize)
            self.log("{n} wins {p}".format(n=name, p=prize))
            updates.append("{n} wins {p}".format(n=name, p=prize))

        self.tell_bots(updates)

    def __remove_dead_players(self):
        for bot in self.living_bots():
            if bot.chips() == 0:
                bot.kill()

    def say_match_updates(self):
        """Info for the start of the match: game type, time, hands, bots"""
        match_info = self.match_timing()
        match_info.extend(self.ante().match_blinds())
        match_info.extend(self.match_game())

        self.tell_bots(match_info)
        self.say_seating()

    def say_seating(self):
        """Tells each bot where they're seated, individual and broadcast
        """
        broadcast = []
        for bot in self.bots:
            name = bot.state.name
            seat = bot.state.seat
            self.tell_bot(name, ['Settings your_bot {name}'.format(name=name)])
            broadcast.append('{name} seat {seat}'.format(name=name, seat=seat))
        self.tell_bots(broadcast)

    def say_hands(self, bot_hands):
        for bot, hand in bot_hands.iteritems():
            hand_string = cards.to_aigames_list(hand)
            hand_line = '{b} hand {h}'.format(b=bot, h=hand_string)
            self.tell_bot(bot, [hand_line])

    def say_round_updates(self):
        round_updates = []
        for bot in self.bots:
            round_updates.append(
                "{n} stack {s}".format(n=bot.name(), s=bot.chips())
            )
            round_updates.append("Match round {}".format(self.current_round))
        self.tell_bots(round_updates)

    def say_action(self, bot, action):
        """Tells the bots that one of them has performed an action"""
        b = TheAiGameActionBuilder()
        action_string = b.to_string(action)
        self.tell_bots(["{b} {a}".format(b=bot, a=action_string)])

    def say_table_cards(self, dealt_cards):
        """Tells the bots about table cards"""
        table_list = \
            'Match table {}'.format(cards.to_aigames_list(dealt_cards))
        self.tell_bots([table_list])

    def get_time_for_move(self, bot_name):
        bot = self.bot_from_name(bot_name)
        timebank = bot.state.timebank if bot else 0
        return timebank + self.TIME_PER_MOVE

    def notify_bots_turn(self, bot_name):
        timebank = self.get_time_for_move(bot_name) * 1000
        self.tell_bot(
            bot_name, ['Action {b} {t}'.format(b=bot_name, t=timebank)]
        )

    def get_parsed_action(self, line):
        return TheAiGameActionBuilder().from_string(line)

    def get_action(self, bot_name, callback):
        """Handled by subclasses"""
        pass

    def skipped(self, bot_name, deferred):
        """Placeholder in case we want to tell a bot we skipped them"""
        pass

    def tell_bot(self, bot_name, lines):
        """Tells one bot something"""
        bot = self.bot_from_name(bot_name)
        self.__tell_bot(bot, lines)

    def tell_bots(self, lines, silently=False):
        """Tell all bots something through STDIN"""
        for bot in self.bots:
            self.__tell_bot(bot, lines, silently)
            silently = True

    def __tell_bot(self, bot, lines, silently=False):
        """Pass a message to a LoadedBot"""
        for line in lines:
            bot.tell(line)
            if not silently:
                self.log("Telling {b}: {l}".format(b=bot.state.name, l=line))

    def post_bet(self, bot_name, amount):
        """Removes money from a bot stack, returns how much was removed"""
        bot = self.bot_from_name(bot_name)
        chips = bot.chips()
        if chips <= amount:
            self.log("posted an all-in bet for {}".format(bot_name))
            bot.change_chips(chips * -1)
            return chips
        bot.change_chips(amount * -1)
        return amount

    def refund(self, bot_name, amount):
        """Returns money to a bot after an illegal bet"""
        bot = self.bot_from_name(bot_name)
        bot.change_chips(amount)

    def is_all_in(self, bot_name):
        """Returns True if a bot is all in (has no chips left)"""
        bot = self.bot_from_name(bot_name)
        return bot.chips() == 0

    def write_hand_log(self, hand_log):
        if not self.output_directory or not self.key:
            return
        log_dir = os.path.join(self.output_directory, self.key)
        mkdir_p(log_dir)
        hand_file = "hand_{}.json".format(self.current_round)
        try:
            target = os.path.join(log_dir, hand_file)
            log_file = open(target, 'w')
            hand_log.to_file(log_file)
        except IOError as e:
            self.log("Error writing log file: {}".format(e))
        finally:
            log_file.close()


class MatchResults(object):
    def __init__(self, arena):
        self.hands = arena.current_round
        self.starting_stack = 1000  # TODO constant
        self.bots = [
            {"key": b.state.source, "stack": b.state.stack}
            for b in arena.bots
        ]

    def to_dict(self):
        return {
            "hands": self.hands,
            "starting_stack": self.starting_stack,
            "bots": self.bots,
        }
