from trader.indicator.MACD import MACD
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.lib.Crossover import Crossover
from trader.lib.struct.SigType import SigType
from trader.lib.struct.SignalBase import SignalBase


class MACD_Crossover(SignalBase):
    def __init__(self,accnt=None, symbol=None, asset_info=None, kdb=None, win_short=12, win_med=26, win_long=50):
        super(MACD_Crossover, self).__init__(accnt, symbol, asset_info, kdb)
        self.signal_name = "MACD_Crossover"
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.obv = OBV()
        self.ema12 = EMA(self.win_short, scale=24)
        self.ema26 = EMA(self.win_med, scale=24, lag_window=5)
        self.ema50 = EMA(self.win_long, scale=24, lag_window=5)
        self.obv_ema12 = EMA(self.win_short, scale=24)
        self.obv_ema26 = EMA(self.win_med, scale=24, lag_window=5)
        self.obv_ema50 = EMA(self.win_long, scale=24, lag_window=5)
        self.macd = MACD(scale=24)
        self.macd_cross = Crossover(window=10)
        self.macd_zero_cross = Crossover(window=10)

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

    def pre_update(self, kline):
        close = kline.close
        volume = kline.volume
        ts = kline.ts

        if self.min_price == 0 or close < self.min_price:
            self.min_price = close

        if self.max_price == 0 or close > self.max_price:
            self.max_price = close

        self.ts = ts

        obv_value = self.obv.update(close=close, volume=volume)
        self.prev_low = self.low
        self.prev_high = self.high

        self.ema12.update(close)
        value2 = self.ema26.update(close)
        value3 = self.ema50.update(close)
        self.obv_ema12.update(obv_value)
        self.obv_ema26.update(obv_value)
        self.obv_ema50.update(obv_value)

        self.macd.update(close)
        self.macd_cross.update(self.macd.result, self.macd.signal.result)
        self.macd_zero_cross.update(self.macd.result, 0)

    def post_update(kline):
        pass

    def buy_signal(self):
        if self.macd.result == 0 or self.macd.signal.result == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
            return False

        if self.obv_ema26.result <= self.obv_ema26.last_result and self.ema26.result <= self.ema26.last_result:
            return False

        if self.obv_ema12.result <= self.obv_ema12.last_result and self.ema12.result <= self.ema12.last_result:
            return False

        if self.macd_cross.crossup_detected():
            self.buy_type = SigType.SIGNAL_SHORT
            return True

        if self.macd_zero_cross.crossup_detected():
            self.buy_type = SigType.SIGNAL_SHORT
            return True

        return False

    def sell_signal(self):
        if self.macd.result == 0 or self.macd.signal.result == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema12.result > self.obv_ema12.last_result and self.ema12.result > self.ema12.last_result:
            return False

        if self.macd_cross.crossdown_detected():
            self.sell_type = SigType.SIGNAL_SHORT
            return True

        if self.macd_zero_cross.crossdown_detected():
            self.sell_type = SigType.SIGNAL_SHORT
            return True

        return False
