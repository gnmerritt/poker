from __future__ import division

import os, sys

def fix_paths():
    """Hack to set up PYTHONPATH"""
    poker_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(poker_dir)

def get_data_file(filename):
    top_source_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    data_dir = os.path.join(top_source_dir, 'data')
    return os.path.join(data_dir, filename)

class MathUtils(object):
    """Math utilities!"""

    @staticmethod
    def percentage(num, denom):
        if denom == 0:
            return 0
        return (num / denom) * 100.0
