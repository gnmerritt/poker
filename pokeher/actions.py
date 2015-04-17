

class GameAction(object):
    """Actions a bot can take"""
    FOLD = 0
    CALL = 1
    RAISE = 2
    CHECK = 3

    NAMES = ['F', 'C', 'R', 'C']

    def __init__(self, action, amount=0):
        self.action = action
        self.amount = amount

    def __match(self, query):
        return query == self.action

    def is_fold(self):
        return self.__match(self.FOLD)

    def is_call(self):
        return self.__match(self.CALL)

    def is_raise(self):
        return self.__match(self.RAISE)

    def is_check(self):
        return self.__match(self.CHECK)

    def __repr__(self):
        return "<GameAction type={}, amount={}>" \
          .format(self.NAMES[self.action], self.amount)
