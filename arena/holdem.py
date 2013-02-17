import random
import pokeher.cards as cards

class Holdem(object):
    """Texas Hold'em. Two hole cards, 5 table cards dealt 3-1-1"""
    def min_players(self):
        """Can be played 1-1 (heads up), or up to 10 players at once"""
        return 2

    def max_players(self):
        return 10

    def hand_size(self):
        return 2

    def play_hand(self):
        """Controls state for one hand of hold'em poker"""
        pass

    def deal_hands(self):
        """Deals out hands for players. Returns a tuple ([hands], remaining_deck)"""
        num_bots = self.bot_count()
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
