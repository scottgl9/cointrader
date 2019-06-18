from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.lib.TrendState.TrendStateTrack import TrendStateTrack
from trader.lib.TrendState.TrendStateInfo import TrendStateInfo
from trader.lib.struct.SignalBase import SignalBase


class TrendStateTrack_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, hkdb=None):
        super(TrendStateTrack_Signal, self).__init__(accnt, symbol, asset_info, hkdb)
        self.signal_name = "TrendStateTrack_Signal"
        self.disabled = False
        self.disabled_end_ts = 0
        self.start_timestamp = 0
        self.last_close = 0

        self.tst = TrendStateTrack(smoother=EMA(12, scale=24))
        self.obv = OBV()
        self.obv_ema12 = EMA(12)
        self.obv_ema500 = EMA(50)

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

        #self.obv.update(close, volume, ts)
        #self.obv_ema12.update(self.obv.result, ts)
        #self.obv_ema500.update(self.obv.result, ts)

        self.tst.update(close, ts=ts)

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
        #if (state == TrendStateInfo.STATE_INIT or
        #    state == TrendStateInfo.STATE_NON_TREND_NO_DIRECTION or
        #    state == TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW or
        #    state == TrendStateInfo.STATE_TRENDING_DOWN_SLOW or
        #    state == TrendStateInfo.STATE_TRENDING_DOWN_FAST or
        #    state == TrendStateInfo.STATE_NON_TREND_DOWN_VERY_SLOW or
        #    state == TrendStateInfo.STATE_NON_TREND_DOWN_SLOW or
        #    state == TrendStateInfo.STATE_NON_TREND_DOWN_FAST or
        #    state == TrendStateInfo.STATE_CONT_TREND_DOWN_VERY_SLOW or
        #    state == TrendStateInfo.STATE_CONT_TREND_DOWN_SLOW or
        #    state == TrendStateInfo.STATE_CONT_TREND_DOWN_FAST):
        #    return False

        if (state == TrendStateInfo.STATE_TRENDING_UP_FAST or
            state == TrendStateInfo.STATE_TRENDING_UP_SLOW or
            state == TrendStateInfo.STATE_TRENDING_UP_VERY_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_UP_FAST or
            state == TrendStateInfo.STATE_CONT_TREND_UP_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_UP_VERY_SLOW):
            self.buy_type = "TrendState"
            return True

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
        if state == TrendStateInfo.STATE_CONT_TREND_DOWN_FAST or state == TrendStateInfo.STATE_CONT_TREND_DOWN_SLOW:
            self.sell_type='LongTrendState'
            self.disabled = True
            self.disabled_end_ts = self.timestamp + 1000 * 3600 * 4
            return True
        return False

    def sell_signal(self):
        state = self.tst.get_trend_state()
        if (state == TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW or
            state == TrendStateInfo.STATE_TRENDING_DOWN_SLOW or
            state == TrendStateInfo.STATE_TRENDING_DOWN_FAST or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_VERY_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_SLOW or
            state == TrendStateInfo.STATE_CONT_TREND_DOWN_FAST):
            self.sell_type='TrendState'
            return True

        return False
