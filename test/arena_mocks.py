from pokeher.theaigame import TheAiGameActionBuilder


class MockArena(object):
    """No-op arena object for testing"""
    def __init__(self):
        self.all_ins = {}

    def is_all_in(self, better):
        return better in self.all_ins

    def tell_bots(self, what):
        pass

    def say_action(self, better, action):
        pass

    def get_action(self, better):
        pass

    def refund(self, better, amount):
        pass

    def post_bet(self, better, amount):
        return amount


class ScriptedArena(MockArena):
    def __init__(self, actions):
        super(MockArena, self).__init__()
        self.actions = actions
        self.actions.reverse()

    def get_action(self, better):
        action = self.actions.pop()
        assert better == action[0]
        return TheAiGameActionBuilder().from_string(action[1])
