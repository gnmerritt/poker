from __future__ import division


class MathUtils(object):
    """Math utilities!"""

    @staticmethod
    def percentage(num, denom):
        if denom == 0:
            return 0
        return (num / denom) * 100.0
