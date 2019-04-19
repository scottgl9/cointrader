from .HourlySignalBase import HourlySignalBase
from trader.indicator.EMA import EMA

class Hourly_EMA_Crossover(HourlySignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None):
        super(Hourly_EMA_Crossover, self).__init__(accnt, symbol, asset_info)
        self.ema12 = EMA(12)
        self.ema26 = EMA(26)
        self.ema50 = EMA(50)

    def load(self, klines):
        self.klines = klines

    def process(self):
        for kline in self.klines:
            ts = int(kline['ts'])
            close = float(kline['close'])
            self.ema12.update(close)
            self.ema26.update(close)
            self.ema50.update(close)
