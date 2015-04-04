from betting import BettingRound
from pokeher.actions import GameAction
from pokeher.handscore import HandBuilder

class PokerHand(object):
    """A hand of poker
    Various stages of gameplay are defined here for use among multiple
    specific games of poker
    """
    def betting_round(self, bots=None, br=None):
        """Initiates and runs a betting round.
        Returns a tuple of hand_finished, [remaining_players]
        """
        if bots is None:
            bots = []
        if not br:
            br = BettingRound(bots, {}, pot=self.pot)

        current_better = br.next_better()
        while current_better is not None:
            action = self.parent.get_action(current_better)

            if action is None:
                action = GameAction(GameAction.FOLD)

            if action.is_fold():
                br.post_fold(current_better)
            elif action.is_raise() or action.is_call():
                if self.parent.post_bet(current_better, action.amount):
                    br.post_bet(current_better, action.amount)
                else:
                    br.post_fold(current_better)
            elif action.is_check():
                br.post_bet(current_better, 0)

            self.pot = br.pot
            self.parent.say_action(current_better, action)
            self.parent.tell_bots(br.say_pot())

            current_better = br.next_better()

        remaining = br.remaining_players()
        # A hand ends if only one player remains after betting
        return len(remaining) == 1, remaining

    def showdown(self, bots):
        """
        Returns the player(s) who won the showdown
        """
        bots_hands = {b: self.hands[b] for b in bots}
        showdown = Showdown(bots_hands, self.table_cards)
        return True, showdown.winners


class Showdown(object):
    """Finds the best hand for each bot given their hole and table cards
    Returns a list of winning bot names
    """
    def __init__(self, bot_hands, table_cards):
        self.winners = []
        bot_best_hands = {}
        for bot, hand in bot_hands.iteritems():
            _, score = HandBuilder(hand + table_cards).find_hand()
            bot_best_hands[bot] = score

        best_score = None
        for bot, score in bot_best_hands.iteritems():
            if best_score is None:
                best_score = score
            if score >= best_score:
                if score > best_score:
                    best_score = hand
                    self.winners = []
                self.winners.append(bot)
