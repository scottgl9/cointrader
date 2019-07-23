# Stochastic Oscillator
from trader.lib.struct.IndicatorBase import IndicatorBase
from trader.indicator.SMA import SMA


class STOCH(IndicatorBase):
    def __init__(self, window=14):
        IndicatorBase.__init__(self, use_close=True, use_low=True, use_high=True)
        self.values = []
        self.window = window
        self.age = 0
        self.sma = SMA(3)
        self.K = 0
        self.D = 0
        self.result = 0

    def update(self, close, low=0, high=0, ts=0):
        if len(self.values) < self.window:
            if low == 0 or high == 0:
                self.values.append(float(close))
            else:
                self.values.append([float(low), float(high)])
        else:
            if low == 0 or high == 0:
                self.values[int(self.age)] = float(close)
                lowest_low = min(self.values)
                highest_high = max(self.values)
            else:
                self.values[int(self.age)] = [float(low), float(high)]
                lows = []
                highs = []
                for low, high in self.values:
                    lows.append(low)
                    highs.append(high)
                lowest_low = min(lows)
                highest_high = max(highs)
            self.K = 100.0 * (float(close) - lowest_low) / (highest_high - lowest_low)
            self.D = self.sma.update(self.K)
            self.result = self.D
            self.age = (self.age + 1) % self.window

        return self.result
