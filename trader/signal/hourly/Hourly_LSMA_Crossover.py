from trader.lib.struct.SignalBase import SignalBase
from trader.indicator.LSMA import LSMA


class Hourly_LSMA_Crossover(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, kdb=None):
        super(Hourly_LSMA_Crossover, self).__init__(kdb, accnt, symbol, asset_info, kdb)
        self.name = "Hourly_LSMA_Crossover"
        self.lsma24 = LSMA(24)
        # 1 week LSMA
        self.lsma168 = LSMA(168)
        # 1 month LSMA
        self.lsma720 = LSMA(720)

    def hourly_load(self, hourly_ts=0, pre_load_hours=0, ts=0):
        end_ts = hourly_ts
        start_ts = end_ts - self.accnt.hours_to_ts(pre_load_hours)
        self.klines = self.kdb.get_dict_klines(self.symbol, start_ts=start_ts, end_ts=end_ts)
        for kline in self.klines:
            ts = int(kline['ts'])
            close = float(kline['close'])
            self.lsma24.update(close, ts)
            self.lsma168.update(close, ts)
            self.lsma720.update(close, ts)
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        self.last_hourly_ts = self.first_hourly_ts
