import random

from twisted.internet import defer

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
        return ['Settings arenaVersion 1.1',
                'Settings gameType NLHE',
                'Settings gameMode tournament', ]


class HoldemHand(PokerHand):
    """Texas Hold'em. Two hole cards, 5 table cards dealt 3-1-1"""
    def __init__(self, parent, players):
        PokerHand.__init__(self, parent, players)
        self.hand_phases = [
            self.blinds_and_preflop,
            self.__wrap(self.deal_table_cards), # flop
            self.betting_round,
            self.__wrap(self.deal_table_cards), # turn
            self.betting_round,
            self.__wrap(self.deal_table_cards), # river
            self.betting_round,
            self.__wrap(self.showdown),
        ]

    def __wrap(self, phase_function):
        """Wrapper for phases that can run completely synchronously"""
        d = defer.Deferred()
        def runner():
            result = phase_function()
            d.callback(result)
        def wrapped_phase():
            return d, runner
        return wrapped_phase

    def play_hand(self):
        """Controls state for one hand of hold'em poker
        Returns a deferred that will be fired when the hand ends
        """
        self.hands = self.deal_hands(self.players)
        self.blinds_round = self.post_blinds()
        self.parent.say_hands(self.hands)
        return self.on_hand_over, self.__hand_phase_tick

    def __hand_phase_tick(self):
        """A tick of a holdem hand will resolve one phase of the hand,
        finishing if there is only one player left at the end of the phase"""
        def after_phase(args):
            hand_finished, players = args
            self.players = players
            assert self.players
            self.parent.log("--Ran hand phase {}".format(self.phase))

            if hand_finished:
                self.parent.log("--Hand finished after phase {}".format(self.phase))
                self.parent.silent_update(".")
                self.parent.stats.record(self.pot, self.phase)
                self.winner()
            else:
                self.phase += 1
                self.__hand_phase_tick()

        phase = self.hand_phases[self.phase]
        on_phase_over, run_phase = phase()
        on_phase_over.addCallback(after_phase)
        run_phase()

    def blinds_and_preflop(self):
        return self.betting_round(br=self.blinds_round)

    def post_blinds(self):
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
        return BettingRound(self.players,
                            bets={sb_bot: posted_sb, bb_bot: posted_bb},
                            pot=0,
                            minimum_raise=bb)

    def post_bet(self, bot_name, amount):
        """Posts a bet, returns posted amount"""
        posted = self.parent.post_bet(bot_name, amount)
        self.pot += posted
        return posted

    def deal_hands(self, players):
        """Deals out hands for players. Returns a map of bots to hands"""
        hand_size = self.parent.hand_size()
        hands = {}
        full_deck = cards.full_deck()
        hand_cards = random.sample(full_deck, hand_size * len(players))
        self.deck = [c for c in full_deck if not c in hand_cards]

        for bot in players:
            hand = []
            for _ in range(0, hand_size):
                hand.append(hand_cards.pop())
            hands[bot] = hand

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
        self.parent.say_table_cards(self.table_cards)
        return False, self.players
