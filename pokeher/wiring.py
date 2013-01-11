
class Parser:
    """Parsers handle lines and store data into self.data"""
    def __init__(self, data):
        self._data = data

    def handle_line(self,line):
        pass

class GameParserDelegate:
    """Generic parser delegate - passes lines to workers"""
    def handle_line(self, line):
        """Delegates the line to each worker"""
        for worker in self.workers:
            if worker.handle_line(line):
                return True
        return False

    def set_up(self, data, turn_callback):
        pass
