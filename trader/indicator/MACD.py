from trader.indicator.EMA import EMA

#MACD Line: (12-day EMA - 26-day EMA)
#Signal Line: 9-day EMA of MACD Line

class MACD:
    def __init__(self, short_weight=12.0, long_weight=26.0, signal_weight=9.0):
        self.last_result = 0.0
        self.result = 0.0
        self.shortEMA = 0.0
        self.longEMA = 0.0
        self.diff = 0.0
        self.short_weight = short_weight
        self.long_weight = long_weight
        self.signal_weight = signal_weight
        self.short = EMA(self.short_weight)
        self.long =  EMA(self.long_weight)
        self.signal = EMA(self.signal_weight)
        #self.result_sma = SMA(2)

    def update(self, price):
        self.short.update(price)
        self.long.update(price)
        self.calculateEMAdiff()
        self.signal.update(self.diff)
        self.last_result = self.result
        self.result = self.diff - self.signal.result
        #self.result_sma.update(self.result - self.last_result)

    def calculateEMAdiff(self):
        self.shortEMA = self.short.result
        self.longEMA = self.long.result
        self.diff = self.shortEMA - self.longEMA
