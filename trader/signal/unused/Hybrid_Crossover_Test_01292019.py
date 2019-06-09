# Testing code for complete rewrite of Hybrid_Crossover for better profits
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.lib.MAAvg import MAAvg
from trader.lib.MACross import MACross
from trader.lib.MADiff import MADiff
from trader.lib.PeakValleyDetect import PeakValleyDetect
from trader.lib.MovingTimeSegment.MTSPriceChannel import MTSPriceChannel
from trader.lib.MovingTimeSegment.MTSPercentChangeROC import MTSPercentChangeROC
from trader.lib.struct.SignalBase import SignalBase


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
        self.obv = OBV()
        self.EMA = EMA

        self.ema12 = EMA(12, scale=24)
        self.ema26 = EMA(26, scale=24, lag_window=5)
        self.ema50 = EMA(50, scale=24, lag_window=5)
        self.ema100 = EMA(100, scale=24, lag_window=5)
        self.ema200 = EMA(200, scale=24, lag_window=5)

        self.maavg = MAAvg()
        self.maavg.add(self.ema12)
        self.maavg.add(self.ema26)
        self.maavg.add(self.ema50)

        self.obv_ema12 = EMA(12, scale=24)
        self.obv_ema26 = EMA(26, scale=24, lag_window=5)
        self.obv_ema50 = EMA(50, scale=24, lag_window=5)

        self.tspc_roc = MTSPercentChangeROC(tspc_seconds=3600, roc_seconds=300, smoother=EMA(50, scale=24))

        ctimeout = 1000 * 3600
        self.ema_cross_12_26 = MACross(cross_timeout=ctimeout)
        self.ema_cross_26_50 = MACross(cross_timeout=ctimeout)
        self.ema_cross_50_100 = MACross(cross_timeout=ctimeout)

        self.ema_cross_12_200 = MACross(cross_timeout=ctimeout * 2)
        self.ema_cross_26_200 = MACross(cross_timeout=ctimeout * 2)
        self.ema_cross_50_200 = MACross(cross_timeout=ctimeout * 2)
        self.ema_cross_100_200 = MACross(cross_timeout=ctimeout * 2)

        # reuse MACross from above for extended detection
        self.ema_cross_12_100 = MACross(cross_timeout=ctimeout * 2)
        self.ema_cross_26_100 = MACross(cross_timeout=ctimeout * 2)

        self.obv_ema_cross_12_26 = MACross(cross_timeout=ctimeout)
        self.obv_ema_cross_26_50 = MACross(cross_timeout=ctimeout)

        self.ema_12_cross_tpsc = MACross(cross_timeout=ctimeout)
        self.maavg_cross_ema200 = MACross(cross_timeout=ctimeout * 2)

        self.diff_ema_12_200 = MADiff()

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

        self.obv.update(close=close, volume=volume)
        obv12_result = self.obv_ema12.update(self.obv.result)
        obv26_result = self.obv_ema26.update(self.obv.result)
        obv50_result = self.obv_ema50.update(self.obv.result)

        ema12_result = self.ema12.update(close)
        ema26_result = self.ema26.update(close)
        ema50_result = self.ema50.update(close)
        ema100_result = self.ema100.update(close)
        ema200_result = self.ema200.update(close)

        tspc_result = self.tspc.update(close, ts)

        self.obv_ema_cross_12_26.update(0, ts, ma1_result=obv12_result, ma2_result=obv26_result)
        self.obv_ema_cross_26_50.update(0, ts, ma1_result=obv26_result, ma2_result=obv50_result)

        self.ema_cross_12_26.update(close, ts, ma1_result=ema12_result, ma2_result=ema26_result)
        self.ema_cross_26_50.update(close, ts, ma1_result=ema26_result, ma2_result=ema50_result)

        self.ema_cross_12_100.update(close, ts, ma1_result=ema12_result, ma2_result=ema100_result)
        self.ema_cross_26_100.update(close, ts, ma1_result=ema26_result, ma2_result=ema100_result)
        self.ema_cross_50_100.update(close, ts, ma1_result=ema50_result, ma2_result=ema100_result)

        self.ema_cross_12_200.update(close, ts, ma1_result=ema12_result, ma2_result=ema200_result)
        self.ema_cross_26_200.update(close, ts, ma1_result=ema26_result, ma2_result=ema200_result)
        self.ema_cross_50_200.update(close, ts, ma1_result=ema50_result, ma2_result=ema200_result)
        self.ema_cross_100_200.update(close, ts, ma1_result=ema100_result, ma2_result=ema200_result)

        self.ema_12_cross_tpsc.update(close, ts, ma1_result=ema12_result, ma2_result=tspc_result)

        self.diff_ema_12_200.update(close, ts, ma1_result=ema12_result, ma2_result=ema200_result)


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

        if self.diff_ema_12_200.is_near_current_max(percent=1.0):
            return False

        if self.ema_cross_12_200.is_near_post_crossup_max(percent=1.0):
            return False

        if (self.ema_cross_26_200.cross_up and self.ema_cross_50_200.cross_up and
                self.ema_cross_50_200.ma1_trend_up() and self.ema_cross_50_200.ma2_trend_up()):
            self.buy_type = 'EMA26_200|EMA50_200'
            return True

        if (self.ema_cross_12_200.cross_up and self.ema_cross_26_200.cross_up and
                self.ema_cross_26_200.ma1_trend_up() and self.ema_cross_26_200.ma2_trend_up()):
            self.buy_type = 'EMA12_200|EMA26_200'
            return True

        if self.ema_12_cross_tpsc.cross_up: # and self.tspc.median_trend_up():
            self.buy_type = 'TPSC12'
            return True

        return False

    def sell_long_signal(self):
        if self.buy_price == 0 or self.last_buy_ts == 0:
            return False

        if self.is_currency_pair:
            return False

        # don't do sell long unless price has fallen at least 10%
        if (self.last_close - self.buy_price) / self.buy_price >= -0.1:
            return False

        if self.ema_cross_50_200.cross_down and self.ema_cross_50_200.ma2_trend_down():
            # don't buy back for at least 6 hours after selling at a 5 percent or greater loss
            if (self.last_close - self.buy_price) / self.buy_price < -0.05:
                self.disabled = True
                self.disabled_end_ts = self.timestamp + 1000 * 8 * 3600
                self.sell_type = "LONG:EMA50_200"
            return True

        if (self.ema_cross_12_200.ma1_trend_down() and self.ema_cross_12_200.ma2_trend_down() and
                self.ema_cross_26_100.ma1_trend_down()) and self.ema_cross_26_100.ma2_trend_down():
            # don't buy back for at least 6 hours after selling at a 5 percent or greater loss
            if (self.last_close - self.buy_price) / self.buy_price < -0.05:
                self.disabled = True
                self.disabled_end_ts = self.timestamp + 1000 * 8 * 3600
                self.sell_type = "LONG:EMA12_200|EMA26_200"
            return True

        return False

    def sell_signal(self):
        if self.ema_cross_12_200.cross_down and self.ema_cross_26_200.cross_down and self.ema_cross_50_200.cross_down:
            self.sell_type = 1
            return True

        if self.ema_cross_50_100.cross_down:
            self.sell_type = 'EMA50_100'
            return True

        if self.ema_cross_12_200.cross_down:
            self.sell_type = 'EMA12_200'
            return True

        if self.ema_cross_26_200.cross_down:
            self.sell_type = 'EMA26_200'
            return True

        if self.ema_12_cross_tpsc.cross_down:
            self.sell_type = 'TPSC12'
            return True

        if self.ema_12_cross_tpsc.is_past_current_max(seconds=900, percent=2.0, cutoff=0.03):
            self.sell_type='TPSC12_MAX'
            return True

        return False
