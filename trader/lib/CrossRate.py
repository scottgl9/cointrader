# track rate at which two MAs crossover per indicated time frame
from trader.lib.Crossover2 import Crossover2

class CrossRate(object):
    def __init__(self, seconds=3600, ma1=None, ma2=None):
        self.seconds = seconds
        self.ma1 = ma1
        self.ma2 = ma2
        self.ma1_result = 0
        self.ma2_result = 0
        self.cross = Crossover2(window=10)
        self.cross_list = []
        self.ts = 0
        self.result = 0

    def update(self, value, ts, ma1_result=0, ma2_result=0):
        self.ts = ts
        if self.ma1:
            self.ma1_result = self.ma1.update(value)
        else:
            self.ma1_result = ma1_result

        if self.ma2:
            self.ma2_result = self.ma2.update(value)
        else:
            self.ma2_result = ma2_result

        self.cross.update(self.ma1_result, self.ma2_result)

        if self.cross.crossup_detected():
            self.cross_list.append((ts, 1))
        elif self.cross.crossdown_detected():
            self.cross_list.append((ts, -1))
        else:
            return self.result

        count = 0
        # remove outdated crossovers
        for i in range(0, len(self.cross_list)):
            (cross_ts, dir) = self.cross_list[i]
            if (self.ts - cross_ts) > 1000 * self.seconds:
                break
            count += 1

        self.cross_list = self.cross_list[count:]
        self.result = len(self.cross_list)

        return self.result
