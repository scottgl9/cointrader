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
from trader.lib.MovingTimeSegment.MTSMoveRate import MTSMoveRate
from trader.lib.TrendStateTrack import TrendStateTrack, TrendState
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

        self.tst = TrendStateTrack(smoother=EMA(12, scale=24))
        self.tspc = MTSPriceChannel(minutes=60)
        self.mts_moverate = MTSMoveRate(small_seg_seconds=120, large_seg_seconds=1800)
        self.obv = OBV()
        self.obv_ema12 = EMA(12)
        self.obv_ema500 = EMA(50)

        self.ema12 = EMA(12, scale=24)
        self.ema26 = EMA(26, scale=24)
        self.ema50 = EMA(50, scale=24)
        self.ema200 = EMA(200, scale=24)

        self.macompare = MACompare()

        self.mts_moverate_cross_zero = Crossover2(window=10)

        ctimeout = 1000 * 300
        self.ema_12_cross_tpsc = MACross(cross_timeout=ctimeout)
        #self.obv_ema_cross_12_500 = MACross(cross_timeout=ctimeout)
        self.ema_cross_12_200 = MACross(cross_timeout=ctimeout)
        #self.tspc_roc_cross_zero = MACross(cross_timeout=ctimeout)

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
                self.disabled_end_ts = self.timestamp + 1000 * 500
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

        self.tst.update(close, ts=ts)

        #self.macompare.update([ema12_result, ema26_result, ema50_result, ema200_result])

        tspc_result = self.tspc.update(close, ts)

        #self.mts_moverate.update(close, ts)
        self.ema_cross_12_200.update(close, ts, ma1_result=ema12_result, ma2_result=ema200_result)
        self.ema_12_cross_tpsc.update(close, ts, ma1_result=ema26_result, ma2_result=tspc_result)

    def buy_signal(self):
        if self.is_currency_pair:
            return False
        if self.disabled:
            if self.timestamp > self.disabled_end_ts:
                self.disabled = False
                self.disabled_end_ts = 0
            else:
                return False

        # don't re-buy less than 30 minutes after a sell
        if self.last_sell_ts != 0 and (self.timestamp - self.last_sell_ts) < 1000 * 3600:
            return False

        state = self.tst.get_trend_state()
        if (state == TrendState.STATE_INIT or
            state == TrendState.STATE_NON_TREND_NO_DIRECTION or
            state == TrendState.STATE_TRENDING_DOWN_VERY_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_FAST or
            state == TrendState.STATE_NON_TREND_DOWN_VERY_SLOW or
            state == TrendState.STATE_NON_TREND_DOWN_SLOW or
            state == TrendState.STATE_NON_TREND_DOWN_FAST):
            #state == TrendState.STATE_NON_TREND_UP_VERY_SLOW or
            #state == TrendState.STATE_TRENDING_UP_VERY_SLOW):
            return False

        if self.ema_cross_12_200.cross_up and self.ema_cross_12_200.ma2_trend_up():
            self.buy_type = 'EMA12_200'

        if self.ema_12_cross_tpsc.cross_up:
            self.buy_type = 'TPSC12'
            return True

        if state == TrendState.STATE_TRENDING_UP_FAST or state == TrendState.STATE_TRENDING_UP_SLOW:
            self.buy_type = "TrendState"
            return True

        #if self.mts_moverate_cross_zero.crossup_detected():
        #    self.buy_type = 'MTS_MOVERATE'
        #    return True

        return False

    def sell_long_signal(self):
        if self.buy_price == 0 or self.last_buy_ts == 0:
            return False
        # don't do sell long unless price has fallen at least 5%
        if (self.last_close - self.buy_price) / self.buy_price >= -0.05:
            return False

        if self.tst.state_changed():
            return False

        state = self.tst.get_trend_state()
        if state == TrendState.STATE_CONT_TREND_DOWN_FAST or state == TrendState.STATE_CONT_TREND_DOWN_SLOW:
            self.sell_type='LongTrendState'
            self.disabled = True
            self.disabled_end_ts = self.timestamp + 1000 * 3600 * 4
            return True
        return False

    def sell_signal(self):
        if self.ema_cross_12_200.cross_down:
            self.sell_type = 'EMA12_200'

        if self.ema_12_cross_tpsc.cross_down:
            self.sell_type = 'TPSC12'
            return True

        if self.ema_12_cross_tpsc.is_past_current_max(seconds=600, percent=1.0, cutoff=0.03):
            self.sell_type='TPSC12_MAX'
            return True

        state = self.tst.get_trend_state()
        if (state == TrendState.STATE_TRENDING_DOWN_VERY_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_FAST):
            self.sell_type='TrendState'
            return True

        #if self.mts_moverate_cross_zero.crossdown_detected():
        #    self.sell_type = 'MTS_MOVERATE'
        #    return True

        return False
