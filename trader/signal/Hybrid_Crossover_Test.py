# Testing code for complete rewrite of Hybrid_Crossover for better profits
from trader.indicator.MACD import MACD
from trader.indicator.EMA import EMA
from trader.indicator.ZLEMA import ZLEMA
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI
from trader.indicator.DTWMA import DTWMA
from trader.lib.Crossover2 import Crossover2
from trader.lib.MAAvg import MAAvg
from trader.lib.MACross import MACross
from trader.lib.MADiff import MADiff
from trader.lib.PeakValleyDetect import PeakValleyDetect
from trader.lib.TimePeakValley import TimePeakValley
from trader.lib.MovingTimeSegment.MTSPriceChannel import MTSPriceChannel
from trader.lib.MovingTimeSegment.MTSPercentChangeROC import MTSPercentChangeROC
from trader.signal.SigType import SigType
from trader.signal.SignalBase import SignalBase


class Hybrid_Crossover_Test(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None):
        super(Hybrid_Crossover_Test, self).__init__(accnt, symbol, asset_info)
        self.signal_name = "Hybrid_Crossover_Test"
        self.disabled = False
        self.disabled_end_ts = 0
        self.start_timestamp = 0
        self.last_close = 0

        self.detector = PeakValleyDetect()
        self.tspc = MTSPriceChannel(minutes=60)
        #self.obv = OBV()
        self.EMA = EMA

        self.ema12 = EMA(12, scale=24)

        #self.obv_ema12 = EMA(12, scale=24)
        #self.obv_ema26 = EMA(26, scale=24, lag_window=5)
        #self.obv_ema50 = EMA(50, scale=24, lag_window=5)

        ctimeout = 1000 * 3600
        self.ema_12_cross_tpsc = MACross(cross_timeout=ctimeout)

        #self.diff_ema_12_200 = MADiff()

    def get_cache_list(self):
        if not self.accnt.simulate:
            return None

        return self.cache.get_cache_list()

    def pre_update(self, close, volume, ts, cache_db=None):
        if self.timestamp == 0:
            self.timestamp = ts
            if self.is_currency_pair:
                self.disabled = True
                self.disabled_end_ts = self.timestamp + 1000 * 3600
            #else:
            #    self.disabled = True
            #    self.disabled_end_ts = self.timestamp + 1000 * 1800
        else:
            self.last_timestamp = self.timestamp
            self.timestamp = ts

        self.last_close = close

        ema12_result = self.ema12.update(close)

        tspc_result = self.tspc.update(close, ts)

        self.ema_12_cross_tpsc.update(close, ts, ma1_result=ema12_result, ma2_result=tspc_result)

    def buy_signal(self):
        if self.disabled:
            if self.timestamp > self.disabled_end_ts:
                self.disabled = False
                self.disabled_end_ts = 0
            else:
                return False

        # don't re-buy less than 30 minutes after a sell
        if self.last_sell_ts != 0 and (self.timestamp - self.last_sell_ts) < 1000 * 3600:
            return False

        if self.ema_12_cross_tpsc.cross_up: # and self.tspc.median_trend_up():
            self.buy_type = 'TPSC12'
            return True

        return False

    def sell_long_signal(self):
        return False

    def sell_signal(self):
        if self.ema_12_cross_tpsc.cross_down:
            self.sell_type = 'TPSC12'
            return True

        if self.ema_12_cross_tpsc.is_past_current_max(seconds=900, percent=2.0, cutoff=0.03):
            self.sell_type='TPSC12_MAX'
            return True

        return False
