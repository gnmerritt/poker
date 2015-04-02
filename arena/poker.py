from betting import BettingRound
from pokeher.actions import GameAction


class PokerHand(object):
    """A hand of poker
    Various stages of gameplay are defined here for use among multiple
    specific games of poker
    """
    def betting_round(self, br=None):
        """Initiates and runs betting round"""
        if not br:
            br = BettingRound([], {}, pot=self.pot)
        self.br = br

        current_better = self.br.next_better()
        while current_better is not None:
            action = self.parent.get_action(current_better)

            if action is None:
                action = GameAction(GameAction.FOLD)

            if action.is_fold():
                br.post_fold(current_better)
            elif action.is_raise() or action.is_call():
                br.post_bet(current_better, action.amount)
            elif action.is_check():
                br.post_bet(current_better, 0)

            self.parent.say_action(current_better, action)

            current_better = self.br.next_better()

        return br.remaining_players()

    def showdown(self, highlow=False):
        """"""
        pass
