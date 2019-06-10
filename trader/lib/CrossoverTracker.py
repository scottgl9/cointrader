from trader.lib.MovingTimeSegment.MTSCrossover2 import MTSCrossover2
from trader.lib.Crossover2 import Crossover2


class CrossoverTracker(object):
    def __init__(self, window=0, win_secs=0, hourly_mode=False):
        self.hourly_mode = hourly_mode
        self.win_secs = win_secs
        self.window = window
        self.cross_info_list = []
        if self.hourly_mode:
            self.cross = Crossover2(window=self.window)
        else:
            self.cross = MTSCrossover2(win_secs=self.win_secs)

    def update(self, value1, value2, ts=0):
        self.cross.update(value1=value1, value2=value2, ts=ts)
        if self.cross.crossup_detected():
            cross_info = CrossInfo(self.cross.crossup_value,
                                   self.cross.crossup_ts,
                                   CrossInfo.CROSS_UP)
            self.cross_info_list.append(cross_info)
        elif self.cross.crossdown_detected():
            cross_info = CrossInfo(self.cross.crossdown_value,
                                   self.cross.crossdown_ts,
                                   CrossInfo.CROSS_DOWN)
            self.cross_info_list.append(cross_info)


class CrossInfo(object):
    CROSS_DOWN = -1
    CROSS_UP = 1
    def __init__(self, value, ts, type):
        self.value = value
        self.ts = ts
        self.type = type
