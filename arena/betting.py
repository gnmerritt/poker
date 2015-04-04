

class Blinds(object):
    """Players must post a blind to buy in"""
    def __init__(self, small_blind, big_blind):
        assert big_blind > small_blind
        self.small_blind = small_blind
        self.big_blind = big_blind

    def hand_blinds(self):
        """Prints out the blinds for TheAiGame bots"""
        return ["Match smallBlind {sb}".format(sb=self.small_blind),
                "Match bigBlind {bb}".format(bb=self.big_blind), ]


class BlindManager(object):
    """Keeps track of who posts which blind, when to raise blinds"""
    BLIND_MULTIPLIER = 2

    def __init__(self, hands_per_level, bots):
        self.hands_per_level = hands_per_level
        self.hands_this_level = 0
        self.bots = bots
        self.small_blinds_played = [0]*len(bots)
        self.sb_index = 0
        self.blind = Blinds(10, 20)

    def __wrap_index(self, i):
        return i % len(self.bots)

    def next_sb(self):
        """Returns the amount & next bot to post the small blind"""
        return self.blind.small_blind, self.bots[self.sb_index]

    def next_bb(self):
        """Returns the amount & next bot to post the big blind"""
        index = self.__wrap_index(self.sb_index + 1)
        return self.blind.big_blind, self.bots[index]

    def match_blinds(self):
        return ['Settings handsPerLevel {hp}'.format(hp=self.hands_per_level)]

    def __check_raise_blinds(self):
        if self.hands_this_level >= self.hands_per_level:
            self.hands_this_level = 0
            self.__increment_blinds()

    def __increment_blinds(self):
        new_sb = self.blind.small_blind * self.BLIND_MULTIPLIER
        new_bb = self.blind.big_blind * self.BLIND_MULTIPLIER
        self.blind = Blinds(new_sb, new_bb)

    def finish_hand(self):
        """Called by the game after every hand"""
        self.sb_index = self.__wrap_index(self.sb_index + 1)
        self.hands_this_level += 1
        self.__check_raise_blinds()

    def eliminate_player(self, name):
        """Removes a player from the blind rotation"""
        for i, player in enumerate(self.bots):
            if name == player:
                self.bots[i] = None
                if self.sb_index > i:
                    self.sb_index = self.__wrap_index(self.sb_index - 1)

        self.bots = [b for b in self.bots if b is not None]


class NoBetLimit(object):
    """Players can bet any amount, at any time"""

    def check_bet(self, pot, bet):
        """Returns true if the bet is legal given the current pot"""
        return bet > 0


class BettingRound(object):
    """Controls a round of betting.
    Each player has the chance to check, call, raise or fold.
    Once a player folds (or bets too small) the player is out"""
    def __init__(self, bots, bets=None, pot=0):
        self.pot = pot
        self.sidepot = None
        self.bots = bots  # ordered list of bots
        if bets is None:
            bets = {}
        self.big_blind = max(bets, key=bets.get) if bets else None
        self.bets = bets  # dict bot name => current bet
        self.high_better = None
        self.next_better_index = -1
        self.finished = (len(bots) == 1)

        # Default bets to 0, find high better
        for i, bot in enumerate(self.bots):
            if bot in self.bets:
                bet = self.bets.get(bot)
                self.pot += bet
                self.__process_bet(bet, bot, is_blind=True)
            else:
                self.bets[bot] = 0
                # first bot that hasn't bet yet gets to bet first
                self.__set_better_index(i)

        self.__set_better_index(0)

    def __set_better_index(self, index):
        if self.next_better_index == -1:
            self.next_better_index = index

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
        if self.can_bet(next_better) and not self.finished:
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

    def remaining_players(self):
        return [p for p, _ in self.bets.iteritems()]

    def post_bet(self, player, bet, all_in=False):
        """Record a valid bet for a bot. Returns False if the bot has folded"""
        # Check & update the next better index
        assert(player == self.next_better())
        self.__forward()

        # Special case for calls around to the big blind
        if self.high_better is None and player == self.big_blind \
          and self.sidepot == self.bets[player]:
            self.high_better = self.big_blind
            self.finished = (bet == 0)

        current_bet = self.bets[player] + bet
        if current_bet >= self.sidepot:
            self.pot += bet
            self.__process_bet(current_bet, player)
            return True
        else:
            self.__fold(player)
            return False

    def post_fold(self, player):
        self.__fold(player)
        self.__forward()
        return False

    def __fold(self, player):
        del self.bets[player]
        self.finished = (len(self.bets) == 1)

    def __forward(self):
        self.next_better_index = (self.next_better_index + 1) % len(self.bots)

    def say_pot(self):
        return ['Match pot {self.pot}'.format(self=self),
                'Match sidepots [{self.sidepot}]'.format(self=self), ]
