from .HourlySignalBase import HourlySignalBase
from trader.lib.MachineLearning.HourlyLSTM import HourlyLSTM
import time

class Hourly_LSTM_Signal(HourlySignalBase):
    def __init__(self, hkdb=None, accnt=None, symbol=None, asset_info=None):
        super(Hourly_LSTM_Signal, self).__init__(hkdb, accnt, symbol, asset_info)
        self.batch_size = 32
        self.hourly_lstm = HourlyLSTM(self.hkdb, self.symbol,
                                      simulate_db_filename=self.accnt.simulate_db_filename, batch_size=self.batch_size)

    def load(self, start_ts=0, end_ts=0, ts=0):
        self.hourly_lstm.load(start_ts=0, end_ts=end_ts)
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(end_ts)
        self.last_hourly_ts = self.first_hourly_ts #- self.accnt.hours_to_ts(self.batch_size)

    def update(self, ts):
        #if (ts - self.last_update_ts) < self.accnt.hours_to_ts(1):
        #    return

        hourly_ts = self.accnt.get_hourly_ts(ts)
        if hourly_ts == self.last_hourly_ts:
            return

        self.hourly_lstm.update(hourly_ts=hourly_ts)

        self.last_update_ts = ts
        self.last_hourly_ts = hourly_ts
