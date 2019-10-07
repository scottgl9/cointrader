from trader.lib.struct.SignalBase import SignalBase
from trader.lib.Crossover2 import Crossover2
from trader.indicator.MACD import MACD


class Hourly_MACD_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, kdb=None, short_weight=12.0,
                 long_weight=26.0, signal_weight=9.0, scale=1.0):
        super(Hourly_MACD_Signal, self).__init__(accnt, symbol, asset_info, kdb)
        self.name = "Hourly_MACD_Signal"
        self.short_weight = short_weight
        self.long_weight = long_weight
        self.signal_weight = signal_weight
        self.scale = scale
        self.macd = MACD(self.short_weight, self.long_weight, self.signal_weight, scale=self.scale)
        self.cross = Crossover2(window=12)
        self.cross_zero = Crossover2(window=12)

    def hourly_load(self, hourly_ts=0, pre_load_hours=0, ts=0):
        end_ts = hourly_ts
        start_ts = end_ts - self.accnt.hours_to_ts(pre_load_hours)
        self.klines = self.kdb.get_dict_klines(self.symbol, start_ts=start_ts, end_ts=end_ts)
        for kline in self.klines:
            ts = int(kline['ts'])
            close = float(kline['close'])
            self.macd.update(close)
            self.cross.update(self.macd.result, self.macd.result2, ts)
            self.cross_zero.update(self.macd.result, 0, ts)
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        self.last_hourly_ts = self.first_hourly_ts

    def hourly_update(self, hourly_ts):
        kline = self.kdb.get_dict_kline(self.symbol, hourly_ts)

        # hourly kline not in db yet, wait until next update() call
        if not kline:
            return False

        close = float(kline['close'])
        self.macd.update(close)
        self.cross.update(self.macd.result, self.macd.result2, hourly_ts)
        self.cross_zero.update(self.macd.result, 0, hourly_ts)

    def hourly_buy_signal(self):
        # if self.cross_zero.crossup_detected():
        #     return True
        if self.cross.crossup_detected():
            return True
        return False

    def hourly_sell_long_signal(self):
        return False

    def hourly_sell_signal(self):
        #if self.cross_zero.crossdown_detected():
        #    return True
        if self.cross.crossdown_detected():
            return True
        return False
