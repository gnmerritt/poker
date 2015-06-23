from __future__ import print_function
import time
import math

import pokeher.cards as cards
from pokeher.theaigame import TheAiGameActionBuilder
from bots import LoadedBot
from hand_stats import HandStats


class LocalIOArena(object):
    """Loads Python bots from source folders, sets up IO channels to them"""
    def __init__(self, delay_secs=1, silent=False):
        self.delay_secs = delay_secs
        self.silent = silent
        self.print_bot_output = True
        self.common_setup()

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

    def log(self, message, force=False):
        if not self.silent or force:
            print(message)

    def silent_update(self, message):
        if self.silent:
            print(message, end="")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for bot in self.bots:
            bot.kill()


class PyArena():
    """Manages game state, communication """
    def common_setup(self):
        self.bots = [] # [LoadedBot]
        self.stats = HandStats()

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
        starting_money = sum(b.state.stack for b in self.living_bots())
        current_round = 0

        while len(self.living_bots()) >= self.min_players():
            self.say_round_updates(current_round)
            self.play_hand()
            self.__remove_dead_players()
            current_round += 1
            self.log("after winnings, bot money:")
            for b in self.living_bots():
                self.log("  {} -> {}".format(b.state.name, b.state.stack))
            assert sum(b.state.stack for b in self.living_bots()) == starting_money

        self.say_round_updates(current_round)
        return self.declare_winners()

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
        hand = self.new_hand()
        winners, pot = hand.play_hand()
        self.__update_chips(winners, pot)
        return winners

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

    def say_round_updates(self, current_round):
        round_updates = []
        for bot in self.bots:
            round_updates.append(
                "{n} stack {s}".format(n=bot.name(), s=bot.chips())
            )
            round_updates.append("Match round {}".format(current_round))
        self.tell_bots(round_updates)

    def say_action(self, bot, action):
        """Tells the bots that one of them has performed an action"""
        b = TheAiGameActionBuilder()
        action_string = b.to_string(action)
        self.tell_bots(["{b} {a}".format(b=bot, a=action_string)])

    def say_table_cards(self, dealt_cards):
        """Tells the bots about table cards"""
        table_list = 'Match table {}'.format(cards.to_aigames_list(dealt_cards))
        self.tell_bots([table_list])

    def notify_bots_turn(self, bot_name):
        self.tell_bot(bot_name, ['Action {b} 1000'.format(b=bot_name)])

    def get_action(self, bot_name, callback):
        """Tells a bot to go, waits for a response"""
        # TODO hook up to timing per bot
        self.notify_bots_turn(bot_name)
        bot = self.bot_from_name(bot_name)
        answer = bot.ask()
        if not answer:
            return None
        time, response = answer
        self.log("bot {b} submitted action {a} chips={c} time={t}"
                 .format(b=bot_name, a=response, c=bot.state.stack, t=time))
        action = self.get_parsed_action(response)
        callback(action)

    def get_parsed_action(self, line):
        return TheAiGameActionBuilder().from_string(line)

    def skipped(self, bot_name):
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
