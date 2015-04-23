

class ArenaTiming(object):
    def match_timing(self):
        """Timing information that's printed to the bots at match start"""
        return ['Settings time_bank {tb}'.format(tb=self.time_bank),
                'Settings time_per_move {tph}'.format(tph=self.time_per_hand), ]


class HalfSecondTurns(ArenaTiming):
    time_bank = 5000
    time_per_hand = 500
