from .HourlySignalBase import HourlySignalBase
from trader.lib.MachineLearning.HourlyLSTM import HourlyLSTM
import time

class Hourly_LSTM_Signal(HourlySignalBase):
    def __init__(self, hkdb=None, accnt=None, symbol=None, asset_info=None):
        super(Hourly_LSTM_Signal, self).__init__(hkdb, accnt, symbol, asset_info)
        self.hourly_lstm = HourlyLSTM(self.hkdb, self.symbol, simulate_db_filename=self.accnt.simulate_db_filename)

    def load(self, start_ts=0, end_ts=0, ts=0):
        self.last_update_ts = ts
        print(time.ctime(int(end_ts / 1000)))
        self.hourly_lstm.load(start_ts=0, end_ts=end_ts)

    def update(self, ts):
        if (ts - self.last_update_ts) < self.accnt.hours_to_ts(1):
            return

        self.last_update_ts = ts