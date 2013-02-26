import time


class Timer(object):
    """Simple timer using a with block"""
    def __init__(self):
        pass

    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.secs = time.clock() - self.start
