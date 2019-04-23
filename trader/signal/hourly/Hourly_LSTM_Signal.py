from .HourlySignalBase import HourlySignalBase
from trader.lib.MachineLearning.HourlyLSTM import HourlyLSTM

class Hourly_LSTM_Signal(HourlySignalBase):
    def __init__(self, hkdb=None, accnt=None, symbol=None, asset_info=None):
        super(Hourly_LSTM_Signal, self).__init__(hkdb, accnt, symbol, asset_info)
        self.hourly_lstm = HourlyLSTM(self.hkdb, self.symbol, simulate_db_filename=self.accnt.simulate_db_filename)

    def load(self, start_ts=0, end_ts=0):
        self.klines = self.hkdb.get_dict_klines(self.symbol, end_ts=end_ts)

    def process(self):
        pass

