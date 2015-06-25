from betting import BettingRound
from pokeher.actions import GameAction
from pokeher.handscore import HandBuilder


class PokerHand(object):
    """A hand of poker
    Various stages of gameplay are defined here for use among multiple
    specific games of poker
    """
    def __init__(self, parent, players):
        """Initializes the holdem game components"""
        self.parent = parent
        self.players = players
        self.table_cards = []
        self.pot = 0
        self.phase = 0

    def betting_round(self, bots=None, br=None):
        """Initiates and runs a betting round.
        Returns a tuple of hand_finished, [remaining_players]
        """
        if bots is None:
            bots = []
        if not br:
            br = BettingRound(bots, bets={}, pot=self.pot)
        self.br = br

        return self.tick()

    def tick(self):
        br = self.br
        current_better = br.next_better()
        if current_better is not None:
            self.pot = br.pot
            self.parent.tell_bots(br.say_pot())
            self.parent.tell_bot(current_better, br.say_to_call(current_better))
            self.__handle_bet(br, current_better)
            return self.tick()
        else:
            return self.betting_round_over()

    def handle_refunds(self):
        refunds = self.br.get_refunds()
        for bot, amount in refunds:
            self.parent.refund(bot, amount)

    def betting_round_over(self):
        self.handle_refunds()
        br = self.br
        self.pot = br.pot
        remaining = br.remaining_players()
        # A hand ends if only one player remains after betting
        return len(remaining) == 1, remaining

    def __handle_bet(self, br, current_better):
        if self.parent.is_all_in(current_better):
            # all-in players automatically call
            action = GameAction(GameAction.CALL)
            self.parent.skipped(current_better)
            self.__do_action(br, current_better, action)
        else:
            def action_callback(action):
                self.__do_action(br, current_better, action)
            self.parent.get_action(current_better, action_callback)

    def __do_action(self, br, current_better, action):
        if action is None:
            action = GameAction(GameAction.FOLD)

        to_call = br.to_call(current_better)

        if action.is_fold():
            br.post_fold(current_better)
        elif action.is_raise():
            if action.amount < br.minimum_raise:
                action.amount = br.minimum_raise
            action.amount += to_call
            self.__check_bet(br, current_better, action)
        elif action.is_call():
            action.amount = to_call
            self.__check_bet(br, current_better, action)
        elif action.is_check():
            br.post_bet(current_better, 0)

        self.parent.say_action(current_better, action)

    def __check_bet(self, br, better, action):
        posted = self.parent.post_bet(better, action.amount)
        action.amount = posted
        big_enough_bet = br.check_bet_size(better, posted)

        if big_enough_bet:
            br.post_bet(better, posted)
        else:
            if self.parent.is_all_in(better):
                action.action = GameAction.CALL
                br.post_bet(better, posted, all_in=True)
            else:
                self.parent.refund(better, posted)
                action.action = GameAction.FOLD
                action.amount = 0
                br.post_fold(better)

    def showdown(self, bots):
        """
        Returns the player(s) who won the showdown
        """
        bots_hands = {b: self.hands[b] for b in bots}
        showdown = Showdown(bots_hands, self.table_cards)
        return True, showdown.winners

    def winner(self):
        """Method that runs at the end of a hand. Updates chips, blinds, etc"""
        self.parent.blind_manager.finish_hand()


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
