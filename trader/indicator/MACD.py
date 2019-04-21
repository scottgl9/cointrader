from .IndicatorBase import IndicatorBase
from trader.indicator.EMA import EMA

#MACD Line: (12-day EMA - 26-day EMA)
#Signal Line: 9-day EMA of MACD Line


class MACD(IndicatorBase):
    def __init__(self, short_weight=12.0, long_weight=26.0, signal_weight=9.0, scale=1.0, plot_mode=False, smoother=None):
        IndicatorBase.__init__(self, use_close=True)
        self.last_result = 0.0
        self.result = 0.0
        self.result_signal = 0.0
        self.shortEMA = 0.0
        self.longEMA = 0.0
        self.diff = 0.0
        self.smoother = smoother
        self.short_weight = short_weight
        self.long_weight = long_weight
        self.signal_weight = signal_weight

        if not self.smoother:
            self.smoother = EMA

        self.short = self.smoother(self.short_weight, scale=scale)
        self.long = self.smoother(self.long_weight, scale=scale)
        self.signal = self.smoother(self.signal_weight, scale=scale)
        self.plot_mode = plot_mode
        self.smoother = None

    def update(self, price, ts=0):
        self.shortEMA = self.short.update(price)
        self.longEMA = self.long.update(price)

        if self.shortEMA != 0 and self.longEMA != 0:
            self.diff = self.shortEMA - self.longEMA

        if not self.plot_mode or self.diff != 0:
            self.result_signal = self.signal.update(self.diff)

        self.last_result = self.result

        self.result = self.diff
