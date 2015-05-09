import sys

import utility; utility.fix_paths()
from theaigame_arena import TheAiGameArena


class GauntletArena(object):
    TRIALS = {
        10: [
            "agents/check_fold_bot.py",
        ],
        50: [
            "agents/call_bot.py",
            "agents/raise_bot.py",
            "agents/call_raise_bot.py",
        ],
        # Old versions of this bot
        100: [
            "../old_bots/v18/pokeher/theaigame_bot.py",
            "../old_bots/v30/pokeher/theaigame_bot.py",
        ],
    }
    BOT_LOAD_DELAY_SECS = 0.1

    def __init__(self, challenger, percentage=100):
        self.challenger = challenger
        self.percentage = 100
        self.wins = {}
        self.tries = {}

    def run(self):
        for attempts, enemies in self.TRIALS.items():
            for enemy in enemies:
                if enemy == self.challenger:
                    continue
                print "\nplaying '{}' ({} matches)".format(enemy, attempts)
                for i in range(attempts):
                    winners = self.run_match(challenger, enemy)
                    self.handle_winners(enemy, winners)
                    tries = self.tries.get(enemy, 0)
                    self.tries[enemy] = tries + 1
                    sys.stdout.flush()
                print "\nResults so far: {}".format(self)

    def run_match(self, challenger, enemy):
        with TheAiGameArena(silent=True) as arena:
            arena.delay_secs = self.BOT_LOAD_DELAY_SECS
            arena.print_bot_output = False
            bot_list = [challenger, enemy]
            winners = arena.run(bot_list)
            return [b.state.source for b in winners]

    def handle_winners(self, enemy, winner_filenames):
        wins = self.wins.get(enemy, 0)
        if self.challenger in winner_filenames:
            wins += 1
        self.wins[enemy] = wins

    def __repr__(self):
        lines = []
        lines.append("Challenger: {}".format(self.challenger))
        for enemy, wins in iter(sorted(self.wins.items())):
            tries = self.tries.get(enemy, 0)
            win_percentage = utility.MathUtils.percentage(wins, tries)
            grade = "PASS" if win_percentage >= self.percentage else "FAIL"
            line = "    {g}  {e:^30} - {w}/{a} ({p}%)" \
              .format(g=grade, e=enemy, w=wins, a=tries, p=win_percentage)
            lines.append(line)
        return "\n".join(lines)


if __name__ == '__main__':
    challenger = sys.argv[1]
    percentage = sys.argv[2] if len(sys.argv) > 2 else 100
    print "Starting gauntlet for '{}'".format(challenger)
    arena = GauntletArena(challenger, 100)
    arena.run()
    print "\nGauntlet results:\n {}".format(arena)
