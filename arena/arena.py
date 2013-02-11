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

    def bot_count(self):
        """Returns the current number of loaded bots"""
        return len(self.bots)

    def play_match(self):
        """Plays rounds of poker until all players are eliminated except one"""
        pass
