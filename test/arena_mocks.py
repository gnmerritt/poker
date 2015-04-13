class MockArena(object):
    """No-op arena object for testing"""
    def __init__(self):
        self.all_ins = {}

    def is_all_in(self, better):
        return better in self.all_ins

    def tell_bots(self):
        pass

    def say_action(self, better, action):
        pass

    def get_action(self, better):
        pass

    def refund(self, better, amount):
        pass


class ScriptedArena(MockArena):
    def __init__(self, actions):
        super(MockArena, self).__init__()
        self.actions = actions.reverse()

    def get_action(self, better):
        action = self.actions.pop()
        assert better == action[0]
        return action[1]
