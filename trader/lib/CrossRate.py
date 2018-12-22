# track rate at which two MAs crossover per indicated time frame
from trader.lib.Crossover2 import Crossover2

class CrossRate(object):
    def __init__(self, seconds=300, ma1=None, ma2=None):
        self.seconds = seconds
        self.ma1 = ma1
        self.ma2 = ma2
        self.ma1_result = 0
        self.ma2_result = 0
        self.cross = Crossover2(window=3)
        self.cross_list = []
        self.ts = 0
        self.last_cross_value = 0
        self.cross_value = 0
        self.cross_result = 0
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
            self.last_cross_value = self.cross_value
            self.cross_value = value
            self.cross_list.append(ts) #(ts, 1))
        elif self.cross.crossdown_detected():
            self.last_cross_value = self.cross_value
            self.cross_value = value
            self.cross_list.append(ts) #(ts, -1))

        count = 0
        # remove outdated crossovers
        for i in range(0, len(self.cross_list)):
            cross_ts = self.cross_list[i]
            if (self.ts - cross_ts) < 1000 * self.seconds:
                break
            count += 1

        if count > 0:
            self.cross_list = self.cross_list[count:]

        if self.cross_value > self.last_cross_value:
            self.cross_result += len(self.cross_list)
        elif self.cross_value < self.last_cross_value:
            self.cross_result -= len(self.cross_list)
        self.result = self.cross_result

        return self.result
