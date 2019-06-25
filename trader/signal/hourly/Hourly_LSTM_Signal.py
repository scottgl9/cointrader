from trader.lib.struct.SignalBase import SignalBase
from trader.lib.MachineLearning.HourlyLSTM import HourlyLSTM


class Hourly_LSTM_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, hkdb=None):
        super(Hourly_LSTM_Signal, self).__init__(accnt, symbol, asset_info, hkdb, uses_models=True)
        self.name = "Hourly_LSTM_Signal"
        self.batch_size = 32
        self.hourly_lstm = HourlyLSTM(self.hkdb, self.symbol,
                                      simulate_db_filename=self.accnt.simulate_db_filename, batch_size=self.batch_size)

    def hourly_load(self, start_ts=0, end_ts=0, ts=0):
        self.hourly_lstm.load(model_start_ts=0, model_end_ts=end_ts)
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(end_ts)
        self.last_hourly_ts = self.first_hourly_ts

    def hourly_update(self, hourly_ts):
        #if (ts - self.last_update_ts) < self.accnt.hours_to_ts(1):
        #    return

        #hourly_ts = self.accnt.get_hourly_ts(ts)
        #if hourly_ts == self.last_hourly_ts:
        #    return

        self.hourly_lstm.update(hourly_ts=hourly_ts)

        #self.last_update_ts = ts
        self.last_hourly_ts = hourly_ts
