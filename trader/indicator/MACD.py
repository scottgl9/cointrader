from trader.indicator.EMA import EMA

#MACD Line: (12-day EMA - 26-day EMA)
#Signal Line: 9-day EMA of MACD Line


class MACD:
    def __init__(self, short_weight=12.0, long_weight=26.0, signal_weight=9.0, smoother_weight=0.0, scale=1.0):
        self.last_result = 0.0
        self.result = 0.0
        self.result_signal = 0.0
        self.shortEMA = 0.0
        self.longEMA = 0.0
        self.diff = 0.0
        self.short_weight = short_weight
        self.long_weight = long_weight
        self.signal_weight = signal_weight
        self.smoother_weight = smoother_weight
        self.short = EMA(self.short_weight, scale=scale)
        self.long = EMA(self.long_weight, scale=scale)
        self.signal = EMA(self.signal_weight, scale=scale)
        self.smoother = None

        if self.smoother_weight != 0:
            self.smoother= EMA(self.smoother_weight, scale=scale)


    def update(self, price):
        self.shortEMA = self.short.update(price)
        self.longEMA = self.long.update(price)

        self.diff = self.shortEMA - self.longEMA

        self.result_signal = self.signal.update(self.diff)

        self.last_result = self.result

        if self.smoother:
            self.result = self.smoother.update(self.diff)
        else:
            self.result = self.diff
