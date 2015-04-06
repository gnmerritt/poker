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
            self.pot = br.pot
            self.parent.tell_bots(br.say_pot())
            self.__handle_bet(br, current_better)
            current_better = br.next_better()

        remaining = br.remaining_players()
        # A hand ends if only one player remains after betting
        return len(remaining) == 1, remaining

    def __handle_bet(self, br, current_better):
        action = self.parent.get_action(current_better)

        if action is None:
            action = GameAction(GameAction.FOLD)

        if action.is_fold():
            br.post_fold(current_better)
        elif action.is_raise() or action.is_call():
            if self.parent.post_bet(current_better, action.amount):
                big_enough_bet = br.post_bet(current_better, action.amount)
                if not big_enough_bet:
                    if self.parent.is_all_in(current_better):
                        print "{} is all in!".format(current_better)
                        br.post_bet(current_better, action.amount, all_in=True)
                    else:
                        self.parent.refund(current_better, action.amount)
            else:
                br.post_fold(current_better)
        elif action.is_check():
            br.post_bet(current_better, 0)

        self.parent.say_action(current_better, action)

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
