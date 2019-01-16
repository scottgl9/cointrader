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
from trader.lib.TimeSegmentPriceChannel import TimeSegmentPriceChannel
from trader.lib.IndicatorCache import IndicatorCache
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
        #self.dtwma_close = DTWMA(30)
        #self.dtwma_volume = DTWMA(30)

        #self.tsj = SegmentJump(tsv1_minutes=1, tsv2_minutes=15, up_multiplier=4, down_multiplier=3)
        #self.tpv = TimePeakValley(reverse_secs=600, span_secs=3600)
        self.detector = PeakValleyDetect()
        self.tspc = TimeSegmentPriceChannel(minutes=60)
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

        self.cache = IndicatorCache(symbol=self.symbol)
        if self.accnt.simulate:
            self.cache.create_cache('O12')
            self.cache.create_cache('O26')
            self.cache.create_cache('O50')

            self.cache.create_cache('12')
            self.cache.create_cache('26')
            self.cache.create_cache('50')
            self.cache.create_cache('100')
            self.cache.create_cache('200')

            self.cache.create_cache('TSPC')

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
            self.last_timestamp = self.timestamp
            self.timestamp = ts

        self.last_close = close

        if self.accnt.simulate and cache_db and not self.cache.loaded and not self.cache.init_load:
            self.cache.load_cache_from_db(cache_db)

        # LOAD CACHED INDICATOR RESULTS
        if self.accnt.simulate and cache_db and self.cache.loaded:
            result = self.cache.get_results_from_cache()
            obv12_result = result['O12']
            obv26_result = result['O26']
            obv50_result = result['O50']
            ema12_result = result['12']
            ema26_result = result['26']
            ema50_result = result['50']
            ema100_result = result['100']
            ema200_result = result['200']
            tspc_result = result['TSPC']
        else:
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

        #self.maavg.update()
        #self.maavg_cross_ema200.update(close, ts, ma1_result=self.maavg.result, ma2_result=ema200_result)

        #if self.maavg.result:
        #    self.detector.update(self.maavg.result)

        # SAVE CACHED INDICATOR RESULTS
        if self.accnt.simulate and cache_db and not self.cache.loaded:
            self.cache.add_result_to_cache('O12', ts, obv12_result)
            self.cache.add_result_to_cache('O26', ts, obv26_result)
            self.cache.add_result_to_cache('O50', ts, obv50_result)
            self.cache.add_result_to_cache('12', ts, ema12_result)
            self.cache.add_result_to_cache('26', ts, ema26_result)
            self.cache.add_result_to_cache('50', ts, ema50_result)
            self.cache.add_result_to_cache('100', ts, ema100_result)
            self.cache.add_result_to_cache('200', ts, ema200_result)
            self.cache.add_result_to_cache('TSPC', ts, tspc_result)
            self.cache.write_results_to_cache(cache_db)


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
            self.buy_type = 1
            return True

        if (self.ema_cross_12_200.cross_up and self.ema_cross_26_200.cross_up and
                self.ema_cross_26_200.ma1_trend_up() and self.ema_cross_26_200.ma2_trend_up()):
            self.buy_type = 2
            return True

        if self.ema_12_cross_tpsc.cross_up: # and self.tspc.median_trend_up():
            self.buy_type = 3
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
                self.sell_type = 6
            return True

        if (self.ema_cross_12_200.ma1_trend_down() and self.ema_cross_12_200.ma2_trend_down() and
                self.ema_cross_26_100.ma1_trend_down()) and self.ema_cross_26_100.ma2_trend_down():
            # don't buy back for at least 6 hours after selling at a 5 percent or greater loss
            if (self.last_close - self.buy_price) / self.buy_price < -0.05:
                self.disabled = True
                self.disabled_end_ts = self.timestamp + 1000 * 8 * 3600
                self.sell_type = 7
            return True

        return False

    def sell_signal(self):
        if self.ema_cross_12_200.cross_down and self.ema_cross_26_200.cross_down and self.ema_cross_50_200.cross_down:
            self.sell_type = 1
            return True

        if self.ema_cross_50_100.cross_down:
            if self.ema_cross_50_100.get_pre_crossdown_high_percent() >= 0.1:
                self.sell_type = 2
                return True

        if self.ema_cross_12_200.cross_down:
            if self.ema_cross_12_200.get_pre_crossdown_high_percent() >= 0.1:
                self.sell_type = 3
                return True

        if self.ema_cross_26_200.cross_down:
            if self.ema_cross_12_26.get_pre_crossdown_high_percent() >= 0.1:
                self.sell_type = 4
                return True

        if self.ema_12_cross_tpsc.cross_down:
            if self.ema_cross_12_26.get_pre_crossdown_high_percent() >= 0.1:
                self.sell_type = 5
                return True

        return False
