# my idea of ROC weighted moving average
from trader.lib.struct.IndicatorBase import IndicatorBase


class RMA(IndicatorBase):
    def __init__(self, window=12):
        IndicatorBase.__init__(self, use_close=True)
        self.window = window
        self.last_value = 0
        self.result = 0
        self.values = []
        self.age = 0

    def update(self, value, ts=0):
        if len(self.values) < self.window:
            self.values.append(float(value))
            if len(self.values) == 1:
                self.result = float(value)
                self.age = (self.age + 1) % self.window
                return self.result
            last_value = 0.0
            sum1 = 0.0
            sum2 = 0.0
            for value in self.values:
                if last_value != 0:
                    roc = value / last_value
                    sum1 += roc * value
                    sum2 += roc
                last_value = value
            self.result = sum1 / sum2
        else:
            self.values[int(self.age)] = float(value)

            age = (self.age + 1) % self.window
            last_value = 0.0
            sum1 = 0.0
            sum2 = 0.0
            last_roc = 0
            roc = 0
            while age != self.age:
                if last_value != 0:
                    last_roc = roc
                    if last_value < self.values[int(self.age)]:
                        roc = self.values[int(self.age)] / last_value
                    else:
                        roc = last_value / self.values[int(self.age)]
                    if last_roc < 1/roc:
                        sum1 += roc * self.values[int(self.age)]
                        sum2 += roc
                    else:
                        sum1 += self.values[int(self.age)]
                        sum2 += 1
                last_value = self.values[int(self.age)]
                age = (age + 1) % self.window
            self.result = sum1 / sum2
        self.age = (self.age + 1) % self.window

        return self.result
