#                                         192 hour moving time frame
#+---------------+------------------------------------------------------------------------------------------------+
#|               |              cur 96 hr                                                                         |
#|               +---------------+--------------------------------------------------------------------------------+
#|               |               |            cur 48hr                                                            |
#|               |               +-------------+------------------------------------------------------------------+
#|               |               |             |            cur 24hr                                              |
#|               |               |             +----------------+-------------------------------------------------+
#|               |               |             |                |             cur 12hr                            |
#|               |               |             |                +-------------+-----------------------------------+
#|  prev 96hr    |  prev 48hr    |  prev 24hr  |  prev 12hr     |             |   3hr MTS + 1hr kline (cur 4hr)   |
#|               |               |             |                |  prev 8hr   |-----------------------------------|
#|               |               |             |                |             ||| 1hr kline| mts3 | mts2 | mts1 |||
#+---------------+---------------+-------------+----------------+-------------+-----------------------------------+

from trader.indicator.EMA import EMA
from .MovingTimeSegment import MovingTimeSegment
from .MTSCrossover2 import MTSCrossover2


class MTS_Retracement(object):
    def __init__(self, win_secs=3600, short_smoother=None, symbol=None, accnt=None, kdb=None):
        self.win_secs = win_secs
        self.win_secs = win_secs
        self.smoother = short_smoother
        self.symbol = symbol
        self.accnt = accnt
        self.kdb = kdb
        self.mts1 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False, track_ts=False)
        self.mts2 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False, track_ts=False)
        self.mts3 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False, track_ts=False)

        self.mts1_slope = 0
        self.mts2_slope = 0
        self.mts3_slope = 0
        self._mts1_avg = 0
        self._mts2_avg = 0
        self.cross_up_mts2 = MTSCrossover2(win_secs=60)
        self.cross_down_mts2 = MTSCrossover2(win_secs=60)
        self.cross_up_mts3 = MTSCrossover2(win_secs=60)
        self.cross_down_mts3 = MTSCrossover2(win_secs=60)
        self.result = 0
        self._cross_up_mts2_up = False
        self._cross_up_mts2_down = False
        self._cross_down_mts2_up = False
        self._cross_down_mts2_down = False
        self._cross_up_mts3_up = False
        self._cross_up_mts3_down = False
        self._cross_down_mts3_up = False
        self._cross_down_mts3_down = False
        self._crossup_value = 0
        self._crossdown_value = 0
        self._crossup_ts = 0
        self._crossdown_ts = 0

        # hourly vars
        self.hourly_ema_high = EMA(12)
        self.hourly_ema_low = EMA(12)
        self.hourly_highs = []
        self.hourly_lows = []
        self.pre_load_hours = 192
        self.first_hourly_ts = 0
        self.last_hourly_ts = 0
        self.last_update_ts = 0
        self.klines = None
        self.prev_96hr_low = 0
        self.prev_96hr_high = 0
        self.cur_96hr_low = 0
        self.cur_96hr_high = 0
        self.prev_48hr_low = 0
        self.prev_48hr_high = 0
        self.cur_48hr_low = 0
        self.cur_48hr_high = 0
        self.prev_24hr_low = 0
        self.prev_24hr_high = 0
        self.cur_24hr_low = 0
        self.cur_24hr_high = 0
        self.prev_12hr_low = 0
        self.prev_12hr_high = 0
        self.cur_12hr_low = 0
        self.cur_12hr_high = 0

    def update(self, value, ts):
        result = value
        if self.smoother:
            result = self.smoother.update(value, ts)
        self.update_mts(result, ts)

    def hourly_load(self, hourly_ts=0, pre_load_hours=0, ts=0):
        end_ts = hourly_ts
        start_ts = end_ts - self.accnt.hours_to_ts(self.pre_load_hours - 1)
        klines = self.kdb.get_dict_klines(self.symbol, start_ts=start_ts, end_ts=end_ts)
        if len(klines) < self.pre_load_hours:
            return
        self.klines = klines
        for kline in self.klines:
            low = float(kline['low'])
            high = float(kline['high'])
            self.hourly_ema_low.update(low)
            self.hourly_ema_high.update(high)
            self.hourly_lows.append(self.hourly_ema_low.result)
            self.hourly_highs.append(self.hourly_ema_high.result)
        self.compute_hourly_lows_highs()
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        self.last_hourly_ts = self.first_hourly_ts

    def hourly_update(self, hourly_ts):
        if not self.klines:
            return

        kline = self.kdb.get_dict_kline(self.symbol, hourly_ts)

        # hourly kline not in db yet, wait until next update() call
        if not kline:
            return False

        self.hourly_ema_low.update(float(kline['low']))
        self.hourly_ema_high.update(float(kline['high']))
        self.hourly_lows = self.hourly_lows[1:]
        self.hourly_highs = self.hourly_highs[1:]
        self.hourly_lows.append(self.hourly_ema_low.result)
        self.hourly_highs.append(self.hourly_ema_high.result)

        # remove oldest kline, and add new kline to end
        self.klines = self.klines[1:]
        self.klines.append(kline)

        self.compute_hourly_lows_highs()

        self.last_hourly_ts = hourly_ts
        return False

    def compute_hourly_lows_highs(self):
        self.prev_96hr_low = 0
        self.prev_96hr_high = 0
        self.prev_48hr_low = 0
        self.prev_48hr_high = 0
        self.prev_24hr_low = 0
        self.prev_24hr_high = 0
        self.prev_12hr_low = 0
        self.prev_12hr_high = 0
        self.cur_96hr_low = 0
        self.cur_96hr_high = 0
        self.cur_48hr_low = 0
        self.cur_48hr_high = 0
        self.cur_24hr_low = 0
        self.cur_24hr_high = 0
        self.cur_12hr_low = 0
        self.cur_12hr_high = 0

        for i in range(0, 96):
            if not self.prev_96hr_low or self.hourly_lows[i] < self.prev_96hr_low:
                self.prev_96hr_low = self.hourly_lows[i]
            if self.hourly_highs[i] > self.prev_96hr_high:
                self.prev_96hr_high = self.hourly_highs[i]
        for i in range(96, 192):
            if not self.cur_96hr_low or self.hourly_lows[i] < self.cur_96hr_low:
                self.cur_96hr_low = self.hourly_lows[i]
            if self.hourly_highs[i] > self.cur_96hr_high:
                self.cur_96hr_high = self.hourly_highs[i]

            j = i - 96

            # update prev and cur 48hr lows and highs
            if j < 48:
                if not self.prev_48hr_low or self.hourly_lows[i] < self.prev_48hr_low:
                    self.prev_48hr_low = self.hourly_lows[i]
                if self.hourly_highs[i] > self.prev_48hr_high:
                    self.prev_48hr_high = self.hourly_highs[i]
            else:
                if not self.cur_48hr_low or self.hourly_lows[i] < self.cur_48hr_low:
                    self.cur_48hr_low = self.hourly_lows[i]
                if self.hourly_highs[i] > self.cur_48hr_high:
                    self.cur_48hr_high = self.hourly_highs[i]

            j -= 48
            # update prev and cur 24hr lows and highs
            if j >= 0:
                if j < 24:
                    if not self.prev_24hr_low or self.hourly_lows[i] < self.prev_24hr_low:
                        self.prev_24hr_low = self.hourly_lows[i]
                    if self.hourly_highs[i] > self.prev_24hr_high:
                        self.prev_24hr_high = self.hourly_highs[i]
                else:
                    if not self.cur_24hr_low or self.hourly_lows[i] < self.cur_24hr_low:
                        self.cur_24hr_low = self.hourly_lows[i]
                    if self.hourly_highs[i] > self.cur_24hr_high:
                        self.cur_24hr_high = self.hourly_highs[i]

            j -= 24
            # update prev and cur 12hr lows and highs
            if j >= 0:
                if j < 12:
                    if not self.prev_12hr_low or self.hourly_lows[i] < self.prev_12hr_low:
                        self.prev_12hr_low = self.hourly_lows[i]
                    if self.hourly_highs[i] > self.prev_12hr_high:
                        self.prev_12hr_high = self.hourly_highs[i]
                else:
                    if not self.cur_12hr_low or self.hourly_lows[i] < self.cur_12hr_low:
                        self.cur_12hr_low = self.hourly_lows[i]
                    if self.hourly_highs[i] > self.cur_12hr_high:
                        self.cur_12hr_high = self.hourly_highs[i]

    # handle updates for the three MTS segments
    def update_mts(self, value, ts):
        self.mts1.update(value, ts)
        if not self.mts1.ready():
            return self.result

        self.mts2.update(self.mts1.first_value(), ts)
        if not self.mts2.ready():
            return self.result

        self.cross_up_mts2.update(self.mts1.last_value(), self.mts2.max(), ts)
        self.cross_down_mts2.update(self.mts1.last_value(), self.mts2.min(), ts)

        self.mts1_slope = self.mts1.diff()
        self.mts2_slope = self.mts2.diff()
        self._mts1_avg = self.mts1.get_sum() / self.mts1.get_sum_count()
        self._mts2_avg = self.mts2.get_sum() / self.mts2.get_sum_count()

        if self.cross_up_mts2.crossup_detected():
            self._cross_up_mts2_up = True
            self._cross_down_mts2_down = False
            self._crossup_ts = ts
            self._crossup_value = self.mts1.last_value()
        elif self.cross_up_mts2.crossdown_detected():
            self._cross_up_mts2_down = True

        if self.cross_down_mts2.crossdown_detected():
            self._cross_up_mts2_up = False
            self._cross_down_mts2_down = True
            self._crossdown_ts = ts
            self._crossdown_value = self.mts1.last_value()
        elif self.cross_down_mts2.crossup_detected():
            self._cross_down_mts2_up = True

        self.mts3.update(self.mts2.first_value(), ts)
        if not self.mts3.ready():
            return self.result

        self.mts3_slope = self.mts3.diff()
        self.cross_down_mts3.update(self.mts1.last_value(), self.mts3.min(), ts)
        self.cross_up_mts3.update(self.mts1.last_value(), self.mts3.min(), ts)

        if self.cross_up_mts3.crossup_detected():
            self._cross_up_mts3_up = True
        elif self.cross_up_mts3.crossdown_detected():
            self._cross_up_mts3_down = True

        if self.cross_down_mts3.crossdown_detected():
            self._cross_down_mts3_down = True
        elif self.cross_down_mts3.crossup_detected():
            self._cross_down_mts3_up = True

    def crossup_detected(self, clear=True):
        #if self.cur_12hr_low == self.cur_24hr_low:
        #    return False
        #if self.mts1.min() <= self.cur_24hr_low:
        #    return False
        #if self.mts1.min() <= self.cur_48hr_low:
        #    return False
        #if self.mts1.min() <= self.cur_96hr_low:
        #    return False
        return self.cross_up_mts2_up_detected(clear=clear)

    def crossdown_detected(self, clear=True):
        if self.cross_down_mts2_down_detected(clear=clear):
            return True
        return False

    def crossdown2_detected(self, clear=True):
        return self.cross_down_mts3_down_detected(clear=clear)

    def long_crossdown_detected(self, clear=True):
        #if self.mts1.min() > self.cur_24hr_low:
        #    return False
        #if self.mts1.min() > self.cur_48hr_low:
        #    return False
        #if self.mts1.min() > self.cur_96hr_low:
        #    return False
        if self.mts1.max < self.mts2.min() or self.mts1.max() < self.mts3.min():
            return True
        return False

    def cross_up_mts2_up_detected(self, clear=True):
        result = self._cross_up_mts2_up
        if clear:
            self._cross_up_mts2_up = False
        return result

    def cross_up_mts2_down_detected(self, clear=True):
        result = self._cross_up_mts2_down
        if clear:
            self._cross_up_mts2_down = False
        return result

    def cross_down_mts2_down_detected(self, clear=True):
        result = self._cross_down_mts2_down
        if clear:
            self._cross_down_mts2_down = False
        return result

    def cross_down_mts3_down_detected(self, clear=True):
        result = self._cross_down_mts3_down
        if clear:
            self._cross_down_mts3_down = False
        return result

    def mts1_avg(self):
        return self._mts1_avg

    def mts2_avg(self):
        return self._mts2_avg
