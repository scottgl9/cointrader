# Testing code for complete rewrite of Hybrid_Crossover for better profits
from trader.indicator.MACD import MACD
from trader.indicator.EMA import EMA
from trader.indicator.ZLEMA import ZLEMA
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI
from trader.indicator.DTWMA import DTWMA
from trader.lib.Crossover2 import Crossover2
from trader.lib.MACross import MACross
from trader.lib.PeakValleyDetect import PeakValleyDetect
from trader.lib.TimePeakValley import TimePeakValley
from trader.lib.SegmentJump import SegmentJump
from trader.signal.SigType import SigType
from trader.signal.SignalBase import SignalBase


class Hybrid_Crossover_Test(SignalBase):
    def __init__(self):
        super(Hybrid_Crossover_Test, self).__init__()
        self.signal_name = "Hybrid_Crossover_Test"
        self.disabled = False
        self.disabled_end_ts = 0
        self.start_timestamp = 0
        self.last_close = 0
        #self.dtwma_close = DTWMA(30)
        #self.dtwma_volume = DTWMA(30)

        self.tsj = SegmentJump(tsv1_minutes=1, tsv2_minutes=15, up_multiplier=4, down_multiplier=3)
        self.tpv = TimePeakValley(reverse_secs=600, span_secs=3600)
        self.detector = PeakValleyDetect()
        self.obv = OBV()
        self.EMA = EMA

        cross_timeout = 1000 * 3600
        self.ema_cross_12_26 = MACross(ema_win1=12, ema_win2=26, scale=24, cross_timeout=cross_timeout)
        self.ema_cross_26_50 = MACross(ema_win1=26, ema_win2=50, scale=24, cross_timeout=cross_timeout)
        self.ema_cross_50_100 = MACross(ema_win1=50, ema_win2=100, scale=24, cross_timeout=cross_timeout)
        self.ema_cross_50_200 = MACross(ema_win1=50, ema_win2=200, scale=24)

        # reuse MACross from above for extended detection
        self.ema_cross_12_100 = MACross(ema_win1=12, ema_win2=100, scale=24, cross_timeout=cross_timeout * 2)
        self.ema_cross_26_100 = MACross(ema_win1=26, ema_win2=100, scale=24, cross_timeout=cross_timeout * 2)

        self.obv_ema_cross_12_26 = MACross(ema_win1=12, ema_win2=26, scale=24, cross_timeout=cross_timeout)
        self.obv_ema_cross_26_50 = MACross(ema_win1=26, ema_win2=50, scale=24, cross_timeout=cross_timeout)

    def pre_update(self, close, volume, ts):
        if self.timestamp == 0:
            self.timestamp = ts

            # wait for 1 hour of running before beginning to buy/sell
            #self.disabled = True
            #self.disabled_end_ts = self.timestamp + 1000 * 3600
        else:
            self.timestamp = ts

        self.last_close = close

        #self.tsj.update(close, ts)

        self.obv.update(close=close, volume=volume)
        self.obv_ema_cross_12_26.update(self.obv.result, ts)
        self.obv_ema_cross_26_50.update(self.obv.result, ts, ma1=self.obv_ema_cross_12_26.ma2)

        self.ema_cross_12_26.update(close, ts)
        self.ema_cross_26_50.update(close, ts, ma1=self.ema_cross_12_26.ma2)
        self.ema_cross_50_100.update(close, ts, ma1=self.ema_cross_26_50.ma2)
        self.ema_cross_50_200.update(close, ts, ma1=self.ema_cross_26_50.ma2)

        self.ema_cross_12_100.update(close, ts, ma1=self.ema_cross_12_26.ma1, ma2=self.ema_cross_50_100.ma2)
        self.ema_cross_26_100.update(close, ts, ma1=self.ema_cross_12_26.ma2, ma2=self.ema_cross_50_100.ma2)

        #self.ema100.update(close)
        #self.tpv.update(self.ema100.result, ts)
        #self.detector.update(self.ema_cross_26_50.get_ma2_result())

    def buy_signal(self):
        if self.disabled:
            # disable trading until we have been running at least 1 hour
            #if self.disabled_end_ts == 0:
            #    self.disabled_end_ts = self.timestamp + 1000 * 3600

            if self.timestamp > self.disabled_end_ts:
                self.disabled = False
                self.disabled_end_ts = 0
            else:
                return False

        if self.last_sell_ts != 0 and (self.timestamp - self.last_sell_ts) < 1000 * 3600:
            return False

        #if self.ema_cross_12_100.cross_down and self.ema_cross_26_100.cross_down and self.ema_cross_50_100.cross_down:
        #        return False

        if (self.ema_cross_50_100.cross_up and self.ema_cross_26_50.cross_up and
                self.ema_cross_50_100.ma2_trend_up() and self.ema_cross_26_50.ma2_trend_up()):
            return True

        if (self.ema_cross_12_26.cross_up and self.ema_cross_26_50.cross_up and
                self.ema_cross_12_26.ma2_trend_up() and self.ema_cross_26_50.ma2_trend_up()):
            return True

        if (self.ema_cross_12_26.cross_up and self.obv_ema_cross_12_26.cross_up and
                self.ema_cross_12_26.ma2_trend_up() and self.obv_ema_cross_12_26.ma2_trend_up()):
            if self.ema_cross_12_26.get_pre_crossup_low_percent() >= 0.5:
                return True

        if (self.ema_cross_26_50.cross_up and self.obv_ema_cross_26_50.cross_up and
                self.ema_cross_26_50.ma2_trend_up() and self.obv_ema_cross_26_50.ma2_trend_up()):
            if self.ema_cross_26_50.get_pre_crossup_low_percent() >= 0.5:
                return True

        #if self.detector.valley_detect():
        #    return True

        #if self.tpv.valley_detected():
        #    return True

        #if self.tsj.up_detected():
        #    return True

        return False

    def sell_long_signal(self):
        if self.buy_price == 0 or self.last_buy_ts == 0:
            return False

        # for prices which haven't fallen more than 10%, do extensive checking that the price is actually
        # trending down in the long term
        #if (self.ema_cross_12_100.cross_down and self.ema_cross_12_100.ma2_trend_down() and
        #    self.ema_cross_26_100.cross_down and self.ema_cross_26_100.ma1_trend_down() and
        #    self.ema_cross_50_100.cross_down and self.ema_cross_50_100.ma1_trend_down()):
        #        return True

        # don't do sell long unless price has fallen at least 10%
        if (self.last_close - self.buy_price) / self.buy_price >= -0.1:
            return False

        if self.ema_cross_50_200.cross_down and self.ema_cross_50_200.ma2_trend_down():
            # don't buy back for at least 6 hours after selling at a 5 percent or greater loss
            if (self.last_close - self.buy_price) / self.buy_price < -0.05:
                self.disabled = True
                self.disabled_end_ts = self.timestamp + 1000 * 6 * 3600
            return True

        if (self.ema_cross_12_26.ma1_trend_down() and self.ema_cross_12_26.ma2_trend_down() and
                self.ema_cross_26_50.ma2_trend_down()) and self.obv_ema_cross_26_50.ma2_trend_down():
            # don't buy back for at least 6 hours after selling at a 5 percent or greater loss
            if (self.last_close - self.buy_price) / self.buy_price < -0.05:
                self.disabled = True
                self.disabled_end_ts = self.timestamp + 1000 * 6 * 3600
            return True

        return False

    def sell_signal(self):
        #if self.ema_cross_50_100.cross_down:
        #    return True
        if self.ema_cross_50_100.cross_down and self.ema_cross_50_100.ma2_trend_down():
            if self.ema_cross_50_100.get_pre_crossdown_high_percent() >= 0.1:
                return True

        if self.ema_cross_26_50.cross_down and self.ema_cross_26_50.ma2_trend_down():
            if self.ema_cross_26_50.get_pre_crossdown_high_percent() >= 0.1:
                return True

        if self.ema_cross_12_26.cross_down and self.ema_cross_12_26.ma2_trend_down():
            if self.ema_cross_12_26.get_pre_crossdown_high_percent() >= 0.1:
                return True

        if (self.ema_cross_12_26.ma1_trend_down() and self.ema_cross_12_26.ma2_trend_down() and
                self.ema_cross_26_50.ma2_trend_down()):
            return True
        #if self.detector.peak_detect():
        #    return True

        #if self.tpv.peak_detected():
        #    return True

        #if self.tsj.down_detected():
        #    return True

        return False
