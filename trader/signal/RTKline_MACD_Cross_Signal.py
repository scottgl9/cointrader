from trader.indicator.MACD import MACD
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.lib.Crossover2 import Crossover2
from trader.lib.RTKline import RTKline
from trader.lib.struct.SigType import SigType
from trader.lib.struct.SignalBase import SignalBase


class RTKline_MACD_Cross_Signal(SignalBase):
    def __init__(self,accnt=None, symbol=None, asset_info=None, hkdb=None):
        super(RTKline_MACD_Cross_Signal, self).__init__(accnt, symbol, asset_info, hkdb)
        self.signal_name = "RTKline_MACD_Cross_Signal"
        self.rtkline = RTKline(win_secs=60, symbol=self.symbol)
        self.obv = OBV()
        self.macd = MACD()
        self.macd_cross = Crossover2(window=10)
        self.macd_zero_cross = Crossover2(window=10)

        self.trend_down_count = 0
        self.trend_up_count = 0
        self.trending_up = False
        self.trending_down = False
        self.low = 0
        self.high = 0
        self.prev_low = 0
        self.prev_high = 0
        self.min_price = 0
        self.max_price = 0
        self.ts = 0

    def pre_update(self, close, volume, ts, cache_db=None):
        self.rtkline.update(close, ts, volume)
        if self.rtkline.ready():
            kline = self.rtkline.get_kline()
            self.macd.update(kline.close)
            self.macd_cross.update(self.macd.result, self.macd.signal.result)
            self.macd_zero_cross.update(self.macd.result, 0)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.macd_cross.crossup_detected():
            return True
        return False

    def sell_signal(self):
        if self.macd_cross.crossdown_detected():
            return True
        return False
