from __future__ import division
from pokeher.utility import MathUtils


class HandStats(object):
    HOLDEM_PHASES = [
        "Preflop",
        "", # cards being dealt (ditto below)
        "Flop",
        "",
        "Turn",
        "",
        "River",
        "Showdown",
    ]

    def __init__(self):
        self.pots = []
        self.phases = {}

    def tick(self, pot, phase):
        count = self.phases.get(phase, 0)
        self.phases[phase] = count + 1
        self.pots.append(pot)

    def __repr__(self):
        hands = len(self.pots)
        avg_pot = sum(self.pots) / hands
        stats = ["hands={h}, avg_pot={p:.2f}" \
                 .format(h=hands, p=avg_pot)]
        for i, p in enumerate(self.HOLDEM_PHASES):
            phase_count = self.phases.get(i, 0)
            if phase_count == 0:
                continue
            phase_percent = MathUtils.percentage(phase_count, hands)
            stats.append("{}=({:.2f}%)".format(p, phase_percent))
        return ", ".join(stats)
