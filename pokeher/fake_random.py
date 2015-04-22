import time
import math

def __seed():
    # 1/2 sin(x)/2 has the range 0,1 like we need
    return 0.5 + 0.5 * math.sin(time.clock() * 1000 % 256)

def uniform(lower, upper):
    """Shitty cyclical RNG to fall back on if import random explodes"""
    multiplier = __seed()
    range = upper - lower
    return lower + (float)(range * multiplier)

def sample(population, num_wanted):
    """Shitty random sampling without replacement"""
    population_len = len(population)
    if num_wanted >= population_len:
        return population

    chosen = {}
    picks = []
    picked = 0
    while picked < num_wanted:
        index = math.trunc(uniform(0, population_len - 1))
        if not chosen.get(index):
            chosen[index] = True
            picks.append(index)
            picked += 1

    return [population[p] for p in picks]
