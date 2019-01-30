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
from trader.lib.MACompare import MACompare
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
        self.tspc_roc = MTSPercentChangeROC(tspc_seconds=500, roc_seconds=500, smoother=EMA(12))
        self.obv = OBV()
        self.obv_ema12 = EMA(12)
        self.obv_ema500 = EMA(50)

        self.ema12 = EMA(12, scale=24)
        self.ema26 = EMA(26, scale=24)
        self.ema50 = EMA(50, scale=24)
        self.ema200 = EMA(200, scale=24)

        self.macompare = MACompare()

        ctimeout = 1000 * 3600
        self.ema_12_cross_tpsc = MACross(cross_timeout=ctimeout)
        self.obv_ema_cross_12_500 = MACross(cross_timeout=ctimeout)
        self.ema_cross_12_50 = MACross(cross_timeout=ctimeout)
        self.tspc_roc_cross_zero = MACross(cross_timeout=ctimeout)
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
            else:
                self.disabled = True
                self.disabled_end_ts = self.timestamp + 1000 * 1800
        else:
            self.last_timestamp = self.timestamp
            self.timestamp = ts

        self.last_close = close

        self.obv.update(close, volume, ts)
        self.obv_ema12.update(self.obv.result, ts)
        self.obv_ema500.update(self.obv.result, ts)

        ema12_result = self.ema12.update(close)
        ema26_result = self.ema26.update(close)
        ema50_result = self.ema50.update(close)
        ema200_result = self.ema200.update(close)

        self.macompare.update([ema12_result, ema26_result, ema50_result, ema200_result])

        tspc_result = self.tspc.update(close, ts)
        tspc_roc_result = self.tspc_roc.update(close, ts)

        self.ema_cross_12_50.update(close, ts, ma1_result=ema12_result, ma2_result=ema50_result)
        self.obv_ema_cross_12_500.update(close, ts, ma1_result=self.obv_ema12.result, ma2_result=self.obv_ema500.result)
        self.ema_12_cross_tpsc.update(close, ts, ma1_result=ema26_result, ma2_result=tspc_result)
        self.tspc_roc_cross_zero.update(close, ts, ma1_result=tspc_roc_result, ma2_result=0)

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

        #if self.ema_12_cross_tpsc.ma2_trend_down():
        #    return False

        if self.ema_12_cross_tpsc.cross_up:# and not self.obv_ema_cross_12_500.cross_down:
            #if self.macompare.ma_proximity_test(percent=0.1):
            #    return False
            self.buy_type = 'TPSC12'
            return True

        if self.tspc_roc_cross_zero.cross_up:
            self.buy_type = 'TSPC_ROC'
            return True

        return False

    def sell_long_signal(self):
        return False

    def sell_signal(self):
        if self.ema_12_cross_tpsc.cross_down:
            self.sell_type = 'TPSC12'
            return True

        if self.tspc_roc_cross_zero.cross_down:
            self.sell_type='TSPC_ROC'
            return True

        if self.ema_12_cross_tpsc.is_past_current_max(seconds=600, percent=1.0, cutoff=0.03):
            self.sell_type='TPSC12_MAX'
            return True

        #if self.obv_ema_cross_12_500.cross_down:
        #    self.sell_type='OBVEMA_12_500'
        #    return True
        #if self.obv_ema_cross_12_500.is_past_current_max(seconds=300, percent=1.0, cutoff=0):
        #    self.sell_type='OBVEMA_12_500_MAX'
        #    return True

        return False
