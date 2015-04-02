import random
import pokeher.cards as cards
from betting import BettingRound, BlindManager
from poker import PokerHand

class Holdem(object):
    def new_hand(self):
        """Returns an instance of holdem"""
        return HoldemHand(self, self.living_bot_names())

    def min_players(self):
        """Can be played 1-1 (heads up), or up to 10 players at once"""
        return 2

    def max_players(self):
        return 10

    def hand_size(self):
        return 2

    def init_game(self):
        """Sets up things that last for longer than a hand"""
        self.blind_manager = BlindManager(hands_per_level=10,
                                          bots=self.living_bot_names())

    def ante(self):
        """Returns the ante for this type of poker (blinds)"""
        return self.blind_manager

    def match_game(self):
        """Info for the start of the game."""
        # TODO: split this out so hold'em is separate
        return ['Settings arenaVersion 1.0',
                'Settings gameType NLHE',
                'Settings gameMode tournament', ]


class HoldemHand(PokerHand):
    """Texas Hold'em. Two hole cards, 5 table cards dealt 3-1-1"""
    def __init__(self, parent, players):
        """Initializes the holdem game components"""
        self.parent = parent
        self.players = players
        self.table_cards = []
        self.pot = 0

    def play_hand(self):
        """Controls state for one hand of hold'em poker"""
        bots = self.parent.living_bot_names()
        self.hands = self.deal_hands(len(bots))
        blinds_round = self.post_blinds(bots)
        self.parent.say_hands(bots, self.hands)
        self.betting_round(blinds_round)

        hand_phases = [self.deal_table_cards,
                       self.betting_round,
                       self.deal_table_cards,
                       self.betting_round,
                       self.showdown,
                       self.parent.blind_manager.finish_hand, ]

        for phase in hand_phases:
            pass

    def post_blinds(self, bots):
        """Returns the first betting round & posts the blinds"""
        bm = self.parent.blind_manager
        sb, sb_bot = bm.next_sb()
        bb, bb_bot = bm.next_bb()
        self.post_bet(bb_bot, bb)  # TODO: check blinds too
        # TODO: formatting shouldn't live here
        blinds = [
            '{sb_bot} post {sb}'.format(sb_bot=sb_bot, sb=sb),
            '{bb_bot} post {bb}'.format(bb_bot=bb_bot, bb=bb),
        ]
        self.parent.tell_bots(blinds)
        self.post_bet(sb_bot, sb)
        return BettingRound(bots,
                            bets={sb_bot: sb, bb_bot: bb},
                            pot=(sb + bb))

    def post_bet(self, bot_name, amount):
        """Posts a bet, returns False on failure"""
        canPost = self.parent.post_bet(bot_name, amount)
        if canPost:
            self.pot += amount
            return True
        else:
            return False

    def deal_hands(self, num_bots):
        """Deals out hands for players. Returns the list of hands"""
        hand_size = self.parent.hand_size()
        hands = []
        full_deck = cards.full_deck()
        hand_cards = random.sample(full_deck, hand_size * num_bots)
        self.deck = [c for c in full_deck if not c in hand_cards]

        for i in range(0, num_bots):
            hand = []
            for j in range(0, hand_size):
                hand.append(hand_cards.pop())
            hands.append(hand)

        return hands

    def deal_table_cards(self):
        """Adds table cards and tells bots"""
        if not self.table_cards:
            # the flop
            self.table_cards = random.sample(self.deck, 3)
        elif len(self.table_cards) >= 3:
            # river & turn
            self.table_cards += random.sample(self.deck, 1)

        # update the deck
        self.deck = [c for c in self.deck if c not in self.table_cards]
        self.parent.say_table_cards()
