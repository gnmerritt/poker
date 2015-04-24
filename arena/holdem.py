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
        self.blind_manager = BlindManager(hands_per_level=20,
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
    def play_hand(self):
        """Controls state for one hand of hold'em poker"""
        bots = self.parent.living_bot_names()
        self.hands = self.deal_hands(bots)
        blinds_round = self.post_blinds(bots)
        self.parent.say_hands(self.hands)

        def blinds_and_preflop(bots):
            return self.betting_round(br=blinds_round)

        def winner(bots):
            """Method that runs at the end of a hand. Updates chips, blinds, etc"""
            self.parent.blind_manager.finish_hand()

        hand_phases = [blinds_and_preflop,
                       self.deal_table_cards, # flop
                       self.betting_round,
                       self.deal_table_cards, # turn
                       self.betting_round,
                       self.deal_table_cards, # river
                       self.betting_round,
                       self.showdown]

        for i, phase in enumerate(hand_phases):
            hand_finished, bots = phase(bots)
            assert bots
            self.parent.log("--Ran hand phase {}".format(i))
            if hand_finished:
                self.parent.log("--Hand finished after phase {}".format(i))
                self.parent.silent_update(".")
                winner(bots)
                return bots, self.pot

    def post_blinds(self, bots):
        """Returns the first betting round & posts the blinds"""
        bm = self.parent.blind_manager
        sb, sb_bot = bm.next_sb()
        bb, bb_bot = bm.next_bb()
        posted_bb = self.post_bet(bb_bot, bb)
        posted_sb = self.post_bet(sb_bot, sb)
        # TODO: formatting shouldn't live here
        blinds = [
            'Match on_button {sb}'.format(sb=sb_bot), # TODO only for heads up
            'Match small_blind {sb}'.format(sb=sb),
            'Match big_blind {bb}'.format(bb=bb),
            '{sb_bot} post {sb}'.format(sb_bot=sb_bot, sb=posted_sb),
            '{bb_bot} post {bb}'.format(bb_bot=bb_bot, bb=posted_bb),
        ]
        self.parent.tell_bots(blinds)
        return BettingRound(bots,
                            bets={sb_bot: posted_sb, bb_bot: posted_bb},
                            pot=0,
                            minimum_raise=bb)

    def post_bet(self, bot_name, amount):
        """Posts a bet, returns posted amount"""
        posted = self.parent.post_bet(bot_name, amount)
        self.pot += posted
        return posted

    def deal_hands(self, bots):
        """Deals out hands for players. Returns a map of bots to hands"""
        hand_size = self.parent.hand_size()
        hands = {}
        full_deck = cards.full_deck()
        hand_cards = random.sample(full_deck, hand_size * len(bots))
        self.deck = [c for c in full_deck if not c in hand_cards]

        for bot in bots:
            hand = []
            for _ in range(0, hand_size):
                hand.append(hand_cards.pop())
            hands[bot] = hand

        return hands

    def deal_table_cards(self, bots):
        """Adds table cards and tells bots"""
        if not self.table_cards:
            # the flop
            self.table_cards = random.sample(self.deck, 3)
        elif len(self.table_cards) >= 3:
            # river & turn
            self.table_cards += random.sample(self.deck, 1)

        # update the deck
        self.deck = [c for c in self.deck if c not in self.table_cards]
        self.parent.say_table_cards(self.table_cards)
        return False, bots
