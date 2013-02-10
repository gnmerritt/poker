
class PyArena:
    """Loads Python bots from source folders, sets up IO channels to them"""
    def __init__(self):
        self.bots = []

    def run(self, args):
        for folder in args:
            self.load_bot(folder)
        if self.min_players() <= self.bot_count() <= self.max_players:
            self.play_game()
        else:
            print "Wrong # of bots ({i}) needed {k}-{j}. Can't play" \
              .format(i=self.bot_count(), k=self.min_players(), j=self.max_players())

    def load_bot(self, source_folder):
        print "loading bot from {f}".format(f=source_folder)

    def bot_count(self):
        """Returns the current number of loaded bots"""
        return len(self.bots)
