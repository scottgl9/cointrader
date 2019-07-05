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
    def __init__(self, win_secs=3600, short_smoother=None, symbol=None, accnt=None, hkdb=None):
        self.win_secs = win_secs
        self.win_secs = win_secs
        self.smoother = short_smoother
        self.symbol = symbol
        self.accnt = accnt
        self.hkdb = hkdb
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
        self.pre_load_hours = 192
        self.first_hourly_ts = 0
        self.last_hourly_ts = 0
        self.last_update_ts = 0
        self.klines = None

    def update(self, value, ts):
        result = value
        if self.smoother:
            result = self.smoother.update(value, ts)
        self.update_mts(result, ts)

    def hourly_load(self, hourly_ts=0, pre_load_hours=0, ts=0):
        end_ts = hourly_ts
        start_ts = end_ts - self.accnt.hours_to_ts(self.pre_load_hours)
        self.klines = self.hkdb.get_dict_klines(self.symbol, start_ts=start_ts, end_ts=end_ts)
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        self.last_hourly_ts = self.first_hourly_ts

    def hourly_update(self, hourly_ts):
        kline = self.hkdb.get_dict_kline(self.symbol, hourly_ts)

        # hourly kline not in db yet, wait until next update() call
        if not kline:
            return False

        # remove oldest kline, and add new kline to end
        self.klines = self.klines[1:].append(kline)

        self.last_hourly_ts = hourly_ts
        return False

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
        return self.cross_up_mts2_up_detected(clear=clear)

    def crossdown_detected(self, clear=True):
        if self.cross_down_mts2_down_detected(clear=clear):
            return True
        return False

    def crossdown2_detected(self, clear=True):
        return self.cross_down_mts3_down_detected(clear=clear)

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
