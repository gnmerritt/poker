

class ArenaTiming(object):
    def match_timing(self):
        """Timing information that's printed to the bots at match start"""
        return ['Settings timeBank {tb}'.format(tb=self.time_bank),
                'Settings timePerMove {tph}'.format(self.time_per_hand), ]


class HalfSecondTurns(ArenaTiming):
    time_bank = 5000
    time_per_hand = 500
