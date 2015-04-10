import time, calendar, math

def __seed():
    # 1/2 sin(x)/2 has the range 0,1 like we need
    return 0.5 + 0.5 * math.sin(calendar.timegm(time.gmtime()) % 256)

def uniform(lower, upper):
    """Shitty cyclical RNG to fall back on if import random explodes"""
    multiplier = __seed()
    range = upper - lower
    return lower + (float)(range * multiplier)
