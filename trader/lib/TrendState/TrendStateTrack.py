# Analyze market data, and track trend(s) using a state representation
import json
from trader.lib.LargestPriceChange import LargestPriceChange
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.TrendState.TrendState import TrendState
from trader.lib.TrendState.TrendStateInfo import TrendStateInfo
from trader.indicator.EMA import EMA


# init_state_seconds: time allowed to capture market data before determining state
# max_state_seconds: maximum amount of time that moving data segment accumulates data
# check_state_seconds: interval at which state is check, and determine if move to new state
class TrendStateTrack(object):
    def __init__(self, init_state_seconds=3600,
                       max_state_seconds=(3600 * 12),
                       short_state_seconds=3600,
                       check_state_seconds=300,
                       percent_slow_cutoff=3.0,
                       percent_very_slow_cutoff=1.0,
                       smoother=None):
        self.init_state_seconds = init_state_seconds
        self.max_state_seconds = max_state_seconds
        self.short_state_seconds = short_state_seconds
        self.check_state_seconds = check_state_seconds
        self.percent_slow_cutoff = percent_slow_cutoff
        self.percent_very_slow_cutoff = percent_very_slow_cutoff
        self.trend_state = None
        self.trend_state_list = []
        self.trend_state_short = None
        self.lpc = LargestPriceChange(use_dict=False)
        self.mts_long = MovingTimeSegment(seconds=self.max_state_seconds)
        self.mts_short = MovingTimeSegment(seconds=self.short_state_seconds)
        self.start_ts = 0
        self.check_start_ts = 0
        self.ready = False
        self.smoother = smoother
        self._trend_state_up_cnt = 0
        self._trend_state_down_cnt = 0

    def get_trend_string(self):
        return TrendStateInfo.get_trend_string(self.trend_state.get_state())

    def get_trend_direction(self):
        return self.trend_state.get_direction()

    def get_trend_state(self):
        return self.trend_state.get_state()

    def get_trend_state_up_counter(self):
        return self._trend_state_up_cnt

    def get_trend_state_down_counter(self):
        return self._trend_state_down_cnt

    def update(self, close, ts, volume=0, low=0, high=0):
        if not self.start_ts:
            self.start_ts = ts
        elif not self.ready:
            # check if ready to classify state
            if (ts - self.start_ts) > self.init_state_seconds * 1000:
                self.ready = True

        if self.smoother:
            value = self.smoother.update(close, ts)
        else:
            value = close

        self.mts_long.update(value, ts)
        self.mts_short.update(value, ts)

        # init of state
        if not self.trend_state:
            self.trend_state = TrendState(state=TrendStateInfo.STATE_INIT,
                                          percent_slow_cutoff=self.percent_slow_cutoff,
                                          percent_very_slow_cutoff=self.percent_very_slow_cutoff)

        if not self.ready:
            return

        if self.check_start_ts and (ts - self.check_start_ts) < self.check_state_seconds * 1000:
            return

        self.trend_state = self.process_trend_state(self.trend_state, self.mts_long, value, ts)
        self.trend_state_list.append(self.trend_state.get_state())

        self.check_start_ts = ts

    # process market data received from update(), apply LargestPriceChange algorithm, then re-determine state
    def process_trend_state(self, trend_state, mts, value, ts):
        values = mts.get_values()
        timestamps = mts.get_timestamps()
        self.lpc.reset(values, timestamps)
        self.lpc.divide_price_segments()

        segments = self.lpc.get_price_score_segments()
        if not self.check_segments(segments):
            return trend_state

        trend_state.process_trend_state(segments, value, ts)
        return trend_state

    # check segments data to see if it's ready to be processed by process_trend_state
    def check_segments(self, segments):
        seg_down = None
        seg_up = None
        seg1_down = None
        seg1_up = None
        seg2_down = None
        seg2_up = None
        seg3_down = None
        seg3_up = None

        try:
            seg_down = segments['down']
            seg_up = segments['up']
        except KeyError:
            pass

        try:
            seg1_down = segments[1]['down']
            seg1_up = segments[1]['up']
        except KeyError:
            pass

        try:
            seg2_down = segments[2]['down']
            seg2_up = segments[2]['up']
        except KeyError:
            pass

        try:
            seg3_down = segments[3]['down']
            seg3_up = segments[3]['up']
        except KeyError:
            pass

        if (not seg_down or not seg_up or not seg1_down or not seg1_up or
            not seg2_down or not seg2_up or not seg3_down or not seg3_up):
            return False

        return True

    def get_seg_down_list(self, field=None):
        return self.trend_state.get_seg_down_list(field)

    def get_seg_up_list(self, field=None):
        return self.trend_state.get_seg_up_list(field)

    def get_seg1_down_list(self, field=None):
        return self.trend_state.get_seg1_down_list(field)

    def get_seg1_up_list(self, field=None):
        return self.trend_state.get_seg1_up_list(field)

    def get_seg2_down_list(self, field=None):
        return self.trend_state.get_seg2_down_list(field)

    def get_seg2_up_list(self, field=None):
        return self.trend_state.get_seg2_up_list(field)

    def get_seg3_down_list(self, field=None):
        return self.trend_state.get_seg3_down_list(field)

    def get_seg3_up_list(self, field=None):
        return self.trend_state.get_seg3_up_list(field)
