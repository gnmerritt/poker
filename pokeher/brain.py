from game import *

class Brain:
    """The brain: combines data classes from game.py to make decisions"""
    def __init__(self, bot):
        self.sharedData = {}
        self.bot = bot
        self.parser = bot.set_up_parser(self.sharedData, self.do_turn)

        # Null-out the data
        self.match = Match(self.sharedData)
        self.player = Player(self.sharedData)
        self.round = Round(self.sharedData)

    def parse_line(self, line):
        """Feeds a line to the parsers"""
        success = self.parser.handle_line(line)
        if success:
            self.update()
        else:
            self.bot.log("didn't handle line: " + line + "\n")

    def do_turn(self, timeLeft):
        """Callback for when the brain has to make a decision"""
        self.bot.call(0)

    def update(self):
        self.match.update()
        self.player.update()
        self.round.update()
