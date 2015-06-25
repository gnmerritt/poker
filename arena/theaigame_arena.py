import sys

from twisted.internet import reactor

import utility
utility.fix_paths()

from local_arena import LocalIOArena
from holdem import Holdem
from betting import NoBetLimit
from timing import HalfSecondTurns


class TheAiGameArena(LocalIOArena, Holdem, NoBetLimit, HalfSecondTurns):
    """Arena for testing bots for http://theaigames.com
    Rules are heads-up, no limit hold'em"""
    pass

if __name__ == '__main__':
    with TheAiGameArena() as arena:
        def end_game(ignored):
            reactor.stop()

        def start_game():
            bot_list = sys.argv[1:]
            on_match_complete, play = arena.run(bot_list)
            on_match_complete.addCallback(end_game)
            play()
        reactor.callWhenRunning(start_game)
        reactor.run()
