
class Blinds(object):
    """Players must post a blind to buy in"""
    def __init__(self, small_blind, big_blind):
        assert big_blind > small_blind
        self.small_blind = small_blind
        self.big_blind = big_blind

        self.hands_per_level = 10
        self.hands_this_level = 0

    def hand_blinds(self):
        """Prints out the blinds for TheAiGame bots"""
        return ["Match smallBlind {sb}".format(sb=self.small_blind),
                "Match bigBlind {bb}".format(bb=self.big_blind),]

    def check_raise_blinds(self):
        pass # TODO

    def match_blinds(self):
        return ['Settings handsPerLevel {hpl}'.format(hpl=self.hands_per_level)]

class NoBetLimit(object):
    """Players can bet any amount, at any time"""

    def check_bet(self, pot, bet):
        """Returns true if the bet is legal given the current pot"""
        return bet > 0

class BettingRound(object):
    """Controls a round of betting.
    Each player has the chance to check, call, raise or fold.
    Once a player folds (or bets too small) the player is out"""
    def __init__(self, bots, bets={}):
        self.pot = 0
        self.sidepot = 0
        self.bots = bots
        self.bets = bets
        self.high_better = None
        self.next_better_index = -1

        # Default bets to 0, find high bettor
        for i, bot in enumerate(self.bots):
            if bot in self.bets:
                bet = self.bets.get(bot)
                self.pot += bet
                self.__process_bet(bet, bot, is_blind=True)
            else:
                self.bets[bot] = 0
                # first bot that hasn't bet yet gets to bet first
                if self.next_better_index == -1:
                    self.next_better_index = i

        if self.next_better_index == -1:
            self.next_better_index = 0

    def __process_bet(self, bet, player, is_blind=False):
        if bet > self.sidepot:
            self.sidepot = bet
            # Don't set the high better for blinds - the BB
            # is allowed to raise when the betting comes around
            if not is_blind:
                self.high_better = player
        self.bets[player] = bet

    def next_better(self):
        """Returns the next bettor, or None if the round is over"""
        next_better = self.bots[self.next_better_index]
        if self.can_bet(next_better):
            return next_better
        else:
            return None

    def can_bet(self, player):
        """Returns true if a player can bet right now"""
        # The high bettor can't bet again
        return self.is_staked(player) and player != self.high_better

    def is_staked(self, player):
        """Is a player currently active and betting"""
        return player in self.bets

    def post_bet(self, player, bet):
        """Record a valid bet for a bot. Returns False if the bot has folded"""
        print 'posting {b} from {p}'.format(b=bet, p=player)
        print 'next_better_index = {n} ({b})'.format(n=self.next_better_index, b=self.next_better())

        # Check & update the next better index
        assert(player == self.next_better())
        self.next_better_index = (self.next_better_index + 1) % len(self.bots)

        current_bet = self.bets[player] + bet
        if current_bet >= self.sidepot:
            self.pot += bet
            self.__process_bet(current_bet, player)
            return True
        else:
            del self.bets[player]
            return False

    def say_pot(self):
        return ['Match pot {self.pot}'.format(self=self),
                'Match sidepots [{self.sidepot}]'.format(self=self),]
