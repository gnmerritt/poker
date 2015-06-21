import sys

import utility
utility.fix_paths()

from holdem import Holdem
from betting import NoBetLimit
from arena import PyArena, LocalIOArena
from timing import HalfSecondTurns


class TheAiGameArena(LocalIOArena, PyArena, Holdem, NoBetLimit, HalfSecondTurns):
    """Arena for testing bots for http://theaigames.com
    Rules are heads-up, no limit hold'em"""
    pass

if __name__ == '__main__':
    with TheAiGameArena() as arena:
        bot_list = sys.argv[1:]
        arena.run(bot_list)
