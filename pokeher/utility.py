from __future__ import division

def fix_paths():
    """Hack to set up PYTHONPATH"""
    import os, sys
    poker_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(poker_dir)

class MathUtils(object):
    """Math utilities!"""

    @staticmethod
    def percentage(num, denom):
        if denom == 0:
            return 0
        return (num / denom) * 100.0
