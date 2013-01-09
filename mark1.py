import sys

class MyBot(object):

        def run(self):
                while not sys.stdin.closed:
                        try:
                                rawline = sys.stdin.readline()
                                if len(rawline) == 0:
                                        break
                                line = rawline.strip()
                                parts = line.split()
                                if parts[0] == 'go':
                                        sys.stdout.write('call 0')
                                        sys.stdout.flush()
                        except EOFError:
                                return

        def __init__(self):
                pass

# Following comment needed to make the bot run:
#  __poker_main__
if __name__ == '__main__':
        bot = MyBot()
        bot.run()
