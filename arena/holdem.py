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
        hands, deck = self.deal_hands(len(bots))
        self.post_blinds()

        """
        self.table_card()
        self.betting_round()
        self.table_card()
        self.betting_round()
        self.showdown()
        self.blind_manager.finish_hand()
        """

    def post_blinds (self):
        """Starts off the post_blinds betting round"""
        self.pot = 0
        sb, sb_bot = self.blind_manager.next_sb()
        bb, bb_bot = self.blind_manager.next_bb()

    def betting_round(self):
        """Initiates a betting round"""
        br = BettingRound([], {}, pot=self.pot)

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
