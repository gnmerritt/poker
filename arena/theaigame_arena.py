import sys
sys.path.append('/Users/nathan/sources/poker/') ## TODO fix
from holdem import Holdem
from betting import NoBetLimit
from arena import PyArena
from timing import HalfSecondTurns


class TheAiGameArena(PyArena, Holdem, NoBetLimit, HalfSecondTurns):
    """Arena for testing bots for http://theaigames.com
    Rules are heads-up, no limit hold'em"""
    pass

if __name__ == '__main__':
    arena = TheAiGameArena()
    bot_list = sys.argv[1:]
    arena.run(bot_list)
