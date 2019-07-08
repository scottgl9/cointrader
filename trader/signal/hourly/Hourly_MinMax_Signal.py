from trader.lib.struct.SignalBase import SignalBase
from trader.lib.hourly.HourlyMinMax import HourlyMinMax


class Hourly_MinMax_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, hkdb=None):
        super(Hourly_MinMax_Signal, self).__init__(accnt, symbol, asset_info, hkdb, uses_models=False)
        self.name = "Hourly_MinMax_Signal"
        self.hourly_minmax = HourlyMinMax(self.symbol, self.accnt, self.hkdb)

    def hourly_load(self, hourly_ts=0, pre_load_hours=0, ts=0):
        return self.hourly_minmax.hourly_load(hourly_ts, pre_load_hours, ts)

    def hourly_update(self, hourly_ts):
        return self.hourly_minmax.hourly_update(hourly_ts)

    def hourly_buy_enable(self):
        if self.hourly_minmax.cur_4hr_high < self.hourly_minmax.prev_8hr_low:
            return False
        if self.hourly_minmax.cur_12hr_high < self.hourly_minmax.prev_24hr_low:
            return False
        return True
