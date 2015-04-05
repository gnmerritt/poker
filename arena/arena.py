import time

import pokeher.cards as cards
from pokeher.theaigame import TheAiGameActionBuilder
from bots import LoadedBot


class PyArena(object):
    """Loads Python bots from source folders, sets up IO channels to them"""
    def __init__(self):
        self.bots = [] # [LoadedBot]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for bot in self.bots:
            bot.kill()

    def run(self, args):
        for file in args:
            self.load_bot(file)
        if self.min_players() <= self.bot_count() <= self.max_players:
            print "Have enough bots, starting match in 2s"
            time.sleep(2)
            self.play_match()
        else:
            print "Wrong # of bots ({i}) needed {k}-{j}. Can't play" \
                .format(i=self.bot_count(), k=self.min_players(),
                        j=self.max_players())

    def load_bot(self, source_file):
        """Starts a bot as a subprocess, given its path"""
        seat = self.bot_count()
        print "loading bot {l} from {f}".format(l=seat, f=source_file)
        bot = LoadedBot(source_file, seat)
        if bot and not bot.process.exploded:
            self.bots.append(bot)

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
            assert sum(b.state.stack for b in self.living_bots()) == starting_money
        self.say_round_updates(current_round)

    def play_hand(self):
        """Plays a hand of poker, updating chip counts at the end."""
        hand = self.new_hand()
        self.called = False ## Hack until real actions are hooked up
        winners, pot = hand.play_hand()
        self.__update_chips(winners, pot)
        return winners

    def __update_chips(self, winners, pot):
        num_winners = len(winners)
        prize_per_winner = pot / num_winners
        assert prize_per_winner >= 0
        updates = []

        for name in winners:
            bot = self.bot_from_name(name)
            bot.change_chips(prize_per_winner)
            updates.append("{n} wins {p}".format(n=name, p=prize_per_winner))

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
            self.tell_bot(name, ['Settings yourBot {name}'.format(name=name)])
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

    def get_action(self, bot_name):
        """Tells a bot to go, waits for a response"""
        self.tell_bot(bot_name, ['go 500']) # TODO hook up to timing per bot
        bot = self.bot_from_name(bot_name)
        time, response = bot.ask()
        print "Got response '{}' from {} in {}s".format(response, bot_name, time)
        action = TheAiGameActionBuilder().from_string(response)
        return action

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
                print "Telling {b}: {l}".format(b=bot.state.name, l=line)

    def post_bet(self, bot_name, amount):
        """Removes money from a bot stack, returns how much was removed"""
        bot = self.bot_from_name(bot_name)
        chips = bot.chips()
        if chips < amount:
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
