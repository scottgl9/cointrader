from trader.indicator.EMA import EMA
from trader.indicator.KAMA import KAMA
from trader.indicator.SMMA import SMMA

class SupportResistLevels(object):
    def __init__(self, kwindow=12, win_short=20, win_long=100):
        self.kwindow = kwindow
        self.win_short = win_short
        self.win_long = win_long
        self.ema_low = EMA(6)
        self.ema_high = EMA(6)
        self.klows = []
        self.khighs = []
        self.lows_short = []
        self.highs_short = []
        self.lows_long = []
        self.highs_long = []
        self.kage = 0
        self.age_short = 0
        self.age_long = 0

    def update(self, close, low, high):
        if len(self.klows) < self.kwindow:
            self.klows.append(self.ema_low.update(float(low)))
            self.khighs.append(self.ema_high.update(float(high)))
        else:
            self.klows[int(self.kage)] = self.ema_low.update(float(low))
            self.khighs[int(self.kage)] = self.ema_high.update(float(high))

        if len(self.klows) == self.kwindow and self.kage == 0:
            # handle short window
            if len(self.lows_short) < self.win_short:
                self.lows_short.append(min(self.klows))
                self.highs_short.append(max(self.khighs))
            else:
                self.lows_short[int(self.age_short)] = min(self.klows)
                self.highs_short[int(self.age_short)] = max(self.khighs)

            # handle long window
            if len(self.lows_long) < self.win_long:
                self.lows_long.append(min(self.klows))
                self.highs_long.append(max(self.khighs))
            else:
                self.lows_long[int(self.age_long)] = min(self.klows)
                self.highs_long[int(self.age_long)] = max(self.khighs)

            self.age_short = (self.age_short + 1) % self.win_short
            self.age_long = (self.age_long + 1) % self.win_long

        self.kage = (self.kage + 1) % self.kwindow

        if len(self.lows_short) == 0 or len(self.lows_long) == 0:
            return 0, 0, 0, 0

        short_low = min(self.lows_short)
        short_high = max(self.highs_short)

        long_low = min(self.lows_long)
        long_high = max(self.highs_long)

        return short_low, short_high, long_low, long_high
