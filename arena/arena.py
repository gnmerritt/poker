import subprocess

class BotState(object):
    """Stuff to remember about each bot"""
    def __init__(self, seat):
        self.name = 'bot_{s}'.format(s=seat) # name for communication
        self.seat = seat # seat at table
        self.stack = 0 # amount of chips
        self.stake = 0 # chips bet currently

class LoadedBot(object):
    """Holds an instance of each bot, keeps track of game info about it"""
    def __init__(self, bot, seat):
        self.bot = bot
        self.state = BotState(seat)
        self.is_active = True

    def tell(self, line):
        """Writes to the bot's STDIN"""
        pass # TODO :-(

    def kill(self):
        """Kills the bot"""
        self.is_active = False

class PyArena(object):
    """Loads Python bots from source folders, sets up IO channels to them"""
    def __init__(self):
        self.bots = []

    def run(self, args):
        for file in args:
            self.load_bot(file)
        if self.min_players() <= self.bot_count() <= self.max_players:
            print "Have enough bots, starting match"
            self.play_match()
        else:
            print "Wrong # of bots ({i}) needed {k}-{j}. Can't play" \
              .format(i=self.bot_count(), k=self.min_players(), j=self.max_players())

    def load_bot(self, source_file):
        """Starts a bot as a subprocess, given its path"""
        seat = self.bot_count()
        print "loading bot {l} from {f}".format(l=seat,f=source_file)
        try:
            with open(source_file) as f:
                bot = subprocess.Popen([source_file],
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
                self.bots.append(LoadedBot(bot, seat))
        except IOError as e:
            print "bot file doesn't exist, skipping"
        # TODO: more error catching probably

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
        self.say_match_updates()
        bots = self.living_bots()
        self.init_game()

        while len(bots) >= self.min_players:
            self.say_round_updates()
            winners = self.play_hand()
            self.say_hand_winner(winners)

    def say_match_updates(self):
        """Info for the start of the match: game type, time, hands, bots"""
        match_info = self.match_timing()
        match_info.append(self.ante().match_blinds())
        match_info.append(self.match_game())

        self.tell_bots(match_info)
        self.say_seating()

    def say_seating(self):
        """Tells each bot where they're seated, and tells everyone who's seated where
"""
        broadcast = []
        for bot in self.bots:
            name = bot.state.name
            seat = bot.state.seat
            bot.tell('Settings yourBot {name}'.format(name=name))
            broadcast.append('{name} seat {seat}'.format(name=name, seat=seat))
        self.tell_bots(broadcast)

    def say_round_updates(self):
        pass

    def say_hand_winner(self, winners):
        pass

    def say_table_cards(self):
        """Tells the bots about table cards"""
        pass

    def get_action(self, bot_name):
        """Tells a bot to go, waits for a response"""
        pass

    def tell_bot(self, bot_name, lines):
        """Tells one bot something"""
        bot = self.bot_from_name(bot_name)
        self.__tell_bot(bot, lines)

    def tell_bots(self, lines):
        """Tell all bots something through STDIN"""
        for bot in self.bots:
            self.__tell_bot(bot, lines)

    def __tell_bot(self, bot, lines):
        """Pass a message to a LoadedBot"""
        for line in lines:
            bot.tell(line)
