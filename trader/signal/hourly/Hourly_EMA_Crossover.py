from trader.lib.struct.SignalBase import SignalBase
from trader.lib.Crossover2 import Crossover2
from trader.indicator.EMA import EMA


class Hourly_EMA_Crossover(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, kdb=None):
        super(Hourly_EMA_Crossover, self).__init__(accnt, symbol, asset_info, kdb)
        self.name = "Hourly_EMA_Crossover"
        self.ema12 = EMA(12)
        self.ema26 = EMA(26)
        self.ema50 = EMA(50)
        #self.ema200 = EMA(200)
        self.cross = Crossover2(window=12)
        self.cross2 = Crossover2(window=12)

    def hourly_load(self, hourly_ts=0, pre_load_hours=0, ts=0):
        end_ts = hourly_ts
        start_ts = end_ts - self.accnt.hours_to_ts(pre_load_hours)
        self.klines = self.kdb.get_dict_klines(self.symbol, start_ts=start_ts, end_ts=end_ts)
        for kline in self.klines:
            ts = int(kline['ts'])
            close = float(kline['close'])
            self.ema12.update(close)
            self.ema26.update(close)
            self.ema50.update(close)
            self.cross.update(self.ema12.result, self.ema26.result, ts)
            self.cross2.update(self.ema12.result, self.ema50.result, ts)
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        self.last_hourly_ts = self.first_hourly_ts

    def hourly_update(self, hourly_ts):
        kline = self.kdb.get_dict_kline(self.symbol, hourly_ts)

        # hourly kline not in db yet, wait until next update() call
        if not kline:
            return False

        close = float(kline['close'])
        self.ema12.update(close)
        self.ema50.update(close)
        self.cross.update(self.ema12.result, self.ema26.result, hourly_ts)
        self.cross2.update(self.ema12.result, self.ema50.result, hourly_ts)

    def hourly_buy_signal(self):
        if self.cross2.crossup_detected():
            return True
        if self.cross.crossup_detected():
            return True
        return False

    def hourly_sell_long_signal(self):
        return False

    def hourly_sell_signal(self):
        if self.cross2.crossdown_detected():
            return True
        if self.cross.crossdown_detected():
            return True
        return False
