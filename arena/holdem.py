import random
import pokeher.cards as cards
from betting import BettingRound, Blinds, BlindManager

class Holdem(object):
    """Texas Hold'em. Two hole cards, 5 table cards dealt 3-1-1"""
    def match_game(self):
        """Info for the start of the game."""
        # TODO: split this out so hold'em is separate
        return ['Settings arenaVersion 1.0',
                'Settings gameType NLHE',
                'Settings gameMode tournament',]

    def init_game(self):
        """Initializes the holdem game components"""
        self.blind_manager = BlindManager(hands_per_level=10,
                                          bots=self.living_bot_names())
        self.table_cards = []

    def min_players(self):
        """Can be played 1-1 (heads up), or up to 10 players at once"""
        return 2

    def max_players(self):
        return 10

    def hand_size(self):
        return 2

    def ante(self):
        """Returns the ante for this type of poker (blinds)"""
        return self.blind_manager

    def play_hand(self):
        """Controls state for one hand of hold'em poker"""
        bots = self.living_bot_names()
        self.hands, self.deck = self.deal_hands(len(bots))
        blinds_round = self.post_blinds(bots)
        self.betting_round(blinds_round)

        """
        self.table_card()
        self.betting_round()
        self.table_card()
        self.betting_round()
        self.showdown()
        self.blind_manager.finish_hand()
        """

    def post_blinds (self, bots):
        """Returns the first betting round & posts the blinds"""
        self.pot = 0
        sb, sb_bot = self.blind_manager.next_sb()
        bb, bb_bot = self.blind_manager.next_bb()
        self.post_bet(bb_bot, bb) # TODO: check blinds too
        self.post_bet(sb_bot, sb)
        return BettingRound(bots,
                            bets={ sb_bot : sb, bb_bot : bb},
                            pot=(sb + bb))

    def post_bet(self, bot_name, amount):
        """Posts a bet, returns False on failure"""
        bot = self.bot_from_name(bot_name)
        if not bot or not bot.state.stack >= amount:
            return False

        bot.state.stack -= amount
        self.pot += amount
        return True

    def betting_round(self, br=None):
        """Initiates a betting round"""
        if not br:
            br = BettingRound([], {}, pot=self.pot)

        next_better = br.next_better()
        while next_better is not None:
            action = self.get_action(next_better)
            # TODO: parse & do the action

    def deal_hands(self, num_bots):
        """Deals out hands for players. Returns a tuple ([hands], remaining_deck)"""
        hand_size = self.hand_size()
        hands = []
        full_deck = cards.full_deck()
        hand_cards = random.sample(full_deck, hand_size * num_bots)
        remaining_deck = [c for c in full_deck if not c in hand_cards]

        for i in range(0, num_bots):
            hand = []
            for j in range(0, hand_size):
                hand.append(hand_cards.pop())
            hands.append(hand)

        return hands, remaining_deck

    def table_card(self):
        """Adds table cards and tells bots"""
        if not self.table_cards:
            # the flop
            self.table_cards = random.sample(self.deck, 3)
        elif len(self.table_cards) >= 3:
            # river & turn
            self.table_cards.append(random.sample(self.deck, 1))

        # update the deck
        self.deck = [c for c in deck if c not in self.table_cards]
        self.say_table_cards()
