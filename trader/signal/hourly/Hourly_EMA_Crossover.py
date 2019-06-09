from trader.lib.struct.HourlySignalBase import HourlySignalBase
from trader.indicator.EMA import EMA

class Hourly_EMA_Crossover(HourlySignalBase):
    def __init__(self, hkdb=None, accnt=None, symbol=None, asset_info=None):
        super(Hourly_EMA_Crossover, self).__init__(hkdb, accnt, symbol, asset_info)
        self.name = "Hourly_EMA_Crossover"
        self.ema12 = EMA(12)
        self.ema26 = EMA(26)
        self.ema50 = EMA(50)

    def load(self, start_ts=0, end_ts=0, ts=0):
        self.klines = self.hkdb.get_dict_klines(self.symbol, start_ts=start_ts, end_ts=end_ts)
        for kline in self.klines:
            ts = int(kline['ts'])
            close = float(kline['close'])
            self.ema12.update(close)
            self.ema26.update(close)
            self.ema50.update(close)
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        self.last_hourly_ts = self.first_hourly_ts
