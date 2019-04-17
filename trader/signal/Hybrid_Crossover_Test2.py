try:
    from trader.indicator.native.AEMA import AEMA
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.AEMA import AEMA
    from trader.indicator.EMA import EMA

from trader.indicator.OBV import OBV
from trader.lib.MACross import MACross
from trader.lib.MADiff import MADiff
from trader.lib.MovingTimeSegment.MTSCrossover import MTSCrossover
from trader.lib.MovingTimeSegment.MTSPriceChannel import MTSPriceChannel
from trader.lib.MovingTimeSegment.MTS_LSMA import MTS_LSMA
from trader.signal.SignalBase import SignalBase


class Hybrid_Crossover_Test2(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None):
        super(Hybrid_Crossover_Test2, self).__init__(accnt, symbol, asset_info)
        self.signal_name = "Hybrid_Crossover_Test2"
        self.disabled = False
        self.disabled_end_ts = 0
        self.start_timestamp = 0
        self.last_close = 0
        self.last_volume = 0

        self.tspc = MTSPriceChannel(minutes=60)
        self.obv = OBV()

        self.lsma = MTS_LSMA(3600)
        self.lsma_obv = MTS_LSMA(3600)
        self.aema12 = AEMA(12, scale_interval_secs=60)

        self.ema12 = EMA(12, scale=24)
        self.ema26 = EMA(26, scale=24, lag_window=5)
        self.ema50 = EMA(50, scale=24, lag_window=5)
        self.ema100 = EMA(100, scale=24, lag_window=5)
        self.ema200 = EMA(200, scale=24, lag_window=5)

        self.obv_ema12 = EMA(12, scale=24)
        self.obv_ema26 = EMA(26, scale=24, lag_window=5)
        self.obv_ema50 = EMA(50, scale=24, lag_window=5)

        #self.tspc_roc = MTSPercentChangeROC(tspc_seconds=3600, roc_seconds=300, smoother=EMA(50, scale=24))

        ctimeout = 1000 * 3600
        self.lsma_cross_aema12 = MTSCrossover(result_secs=60)
        self.lsma_slope_cross_zero = MTSCrossover(result_secs=60)
        self.lsma_obv_cross_zero = MTSCrossover(result_secs=3600)
        self.ema_12_cross_tpsc = MACross(cross_timeout=ctimeout)
        self.ema_cross_12_200 = MACross(cross_timeout=ctimeout * 2)
        self.ema_cross_50_200 = MACross(cross_timeout=ctimeout * 2)
        self.ema_cross_26_100 = MACross(cross_timeout=ctimeout * 2)

    def get_cache_list(self):
        if not self.accnt.simulate:
            return None

        return self.cache.get_cache_list()

    def pre_update(self, close, volume, ts, cache_db=None):
        if self.is_currency_pair:
            return False

        if self.timestamp == 0:
            self.timestamp = ts
            if self.is_currency_pair:
                self.disabled = True
                self.disabled_end_ts = self.timestamp + 1000 * 3600
        else:
            self.last_timestamp = self.timestamp
            self.timestamp = ts

        self.last_close = close
        self.last_volume = volume

        self.lsma.update(close, ts)
        self.aema12.update(close, ts)
        self.obv.update(close=close, volume=volume)
        self.lsma_obv.update(self.obv.result, ts)

        if self.lsma_obv.ready():
            self.lsma_obv_cross_zero.update(self.lsma_obv.result, 0, ts)

        if self.lsma.ready():
            self.lsma_cross_aema12.update(self.lsma.result, self.aema12.result, ts)
            self.lsma_slope_cross_zero.update(self.lsma.m, 0, ts)

        ema12_result = self.ema12.update(close)
        ema26_result = self.ema26.update(close)
        ema50_result = self.ema50.update(close)
        ema100_result = self.ema100.update(close)
        ema200_result = self.ema200.update(close)
        tspc_result = self.tspc.update(close, ts)

        self.ema_12_cross_tpsc.update(close, ts, ma1_result=ema12_result, ma2_result=tspc_result)
        self.ema_cross_26_100.update(close, ts, ma1_result=ema26_result, ma2_result=ema100_result)
        self.ema_cross_12_200.update(close, ts, ma1_result=ema12_result, ma2_result=ema200_result)
        self.ema_cross_50_200.update(close, ts, ma1_result=ema50_result, ma2_result=ema200_result)

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

        if self.lsma_obv_cross_zero.crossdown_detected():
            return False

        if self.ema_12_cross_tpsc.cross_down:
            return False

        if self.ema_12_cross_tpsc.is_past_current_max(seconds=300, percent=2.0, cutoff=0.03):
            return False

        if self.lsma_cross_aema12.crossup_detected():
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
        if self.lsma_cross_aema12.crossdown_detected():
            return True

        return False
