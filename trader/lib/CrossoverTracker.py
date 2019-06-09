from trader.lib.MovingTimeSegment.MTSCrossover2 import MTSCrossover2
from trader.lib.Crossover2 import Crossover2


class CrossoverTracker(object):
    def __init__(self, window=0, win_secs=0, hourly_mode=False):
        self.hourly_mode = hourly_mode
        self.win_secs = win_secs
        self.window = window
        if self.hourly_mode:
            self.cross = Crossover2(window=self.window)
        else:
            self.cross = MTSCrossover2(win_secs=self.win_secs)

    def update(self, value1, value2, ts=0):
        self.cross.update(value1=value1, value2=value2, ts=ts)
