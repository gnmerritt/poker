from pokeher.theaigame import TheAiGameActionBuilder


class MockArena(object):
    """No-op arena object for testing"""
    def tell_bots(self, what):
        pass

    def tell_bot(self, who, what):
        pass

    def say_action(self, better, action):
        print "{} performed '{}'".format(better, action)

    def get_action(self, better):
        pass

    def refund(self, better, amount):
        pass

    def post_bet(self, better, amount):
        return amount


class ScriptedArena(MockArena):
    def __init__(self, actions):
        self.actions = actions
        self.actions.reverse()
        self.all_ins = {}

    def is_all_in(self, better):
        return better in self.all_ins

    def post_bet(self, better, amount):
        if better in self.all_ins:
            return self.all_ins[better]
        return amount

    def get_action(self, better):
        if not self.actions:
            return None
        action = self.actions.pop()
        assert better == action[0]
        return TheAiGameActionBuilder().from_string(action[1])
