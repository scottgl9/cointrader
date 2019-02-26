# Analyze market data, and track trend(s) using a state representation
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
        self.trend_state_prev_list = []
        self.trend_state_short = None
        self.lpc = LargestPriceChange(use_dict=True)
        self.mts_long = MovingTimeSegment(seconds=self.max_state_seconds)
        self.mts_short = MovingTimeSegment(seconds=self.short_state_seconds)
        self.start_ts = 0
        self.check_start_ts = 0
        self.ready = False
        self.smoother = smoother

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
            self.trend_state.start_ts = ts
            self.trend_state.start_price = close
            self.trend_state.start_volume = volume
        else:
            self.trend_state.cur_ts = ts
            self.trend_state.cur_price = close
            self.trend_state.cur_volume = volume

        if not self.trend_state_short:
            self.trend_state_short = TrendState(state=TrendStateInfo.STATE_INIT,
                                                percent_slow_cutoff=self.percent_slow_cutoff,
                                                percent_very_slow_cutoff=self.percent_very_slow_cutoff)

        if not self.ready:
            return

        if self.check_start_ts and (ts - self.check_start_ts) < self.check_state_seconds * 1000:
            return

        self.trend_state = self.process_trend_state(self.trend_state, self.mts_long, ts)
        #self.trend_state_short = self.process_trend_state(self.trend_state_short, self.mts_short, ts)
        self.check_start_ts = ts

    def short_state_changed(self, clear=True):
        return self.trend_state_short.has_state_changed()

    def get_short_trend_string(self):
        return TrendStateInfo.get_trend_string(self.trend_state_short.get_state())

    def get_short_trend_direction(self):
        return self.trend_state.direction

    def has_trend_state_changed(self):
        return self.trend_state.has_state_changed()

    def is_in_trend_state(self):
        return self.trend_state.is_in_trend_state()

    def state_changed(self):
        return self.trend_state.has_state_changed()

    def get_trend_state(self):
        return self.trend_state.get_state()

    def get_trend_string(self):
        return TrendStateInfo.get_trend_string(self.trend_state.get_state())

    def get_trend_direction(self):
        return self.trend_state.direction

    # process market data received from update(), apply LargestPriceChange algorithm, then re-determine state
    def process_trend_state(self, trend_state, mts, ts):
        values = mts.get_values()
        timestamps = mts.get_timestamps()
        self.lpc.reset(values, timestamps)
        self.lpc.divide_price_segments()
        seg_down, seg_up = self.lpc.get_largest_price_segment_percents()
        new_start_ts = self.process_lpc_result(timestamps, seg_down, seg_up)
        if new_start_ts:
            mts.remove_before_ts(new_start_ts)
            values = mts.get_values()
            timestamps = mts.get_timestamps()
            self.lpc.reset(values, timestamps)
            self.lpc.divide_price_segments()
            seg_down, seg_up = self.lpc.get_largest_price_segment_percents()

        trend_state.process_trend_segment_state(seg_down, seg_up, ts)
        return trend_state

    # process result from LargestPriceChange (LPC) to determine if we need to re-run LPC
    def process_lpc_result(self, timestamps, seg_down, seg_up):
        new_start_ts = 0
        seg_down_start_ts = int(seg_down['start_ts'])
        seg_up_start_ts = int(seg_up['start_ts'])
        seg_down_end_ts = int(seg_down['end_ts'])
        seg_up_end_ts = int(seg_up['end_ts'])
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        seg_down_diff_ts = seg_down_end_ts - seg_down_start_ts
        seg_up_diff_ts = seg_up_end_ts - seg_up_start_ts

        # if entire down segment precedes entire up segment and down segment size < up segment size,
        # and seg_down_percent > seg_up_percent, remove previous down segment
        if seg_down_end_ts < seg_up_start_ts and seg_down_diff_ts < seg_up_diff_ts:
            if seg_down_percent > seg_up_percent:
                new_start_ts = seg_up_start_ts
        # if entire up segment precedes entire down segment and up segment size < down segment size,
        # and seg_up_percent > seg_down_percent, remove previous up segment
        elif seg_up_end_ts <= seg_down_start_ts and seg_up_diff_ts < seg_down_diff_ts:
            if seg_up_percent > seg_down_percent:
                new_start_ts = seg_down_start_ts
        # if up segment is completely contained within down segment
        #elif seg_down_start_ts < seg_up_start_ts and seg_up_end_ts < seg_down_end_ts:
        #    pass
        # if down segment is completely contained within up segment
        #elif seg_up_start_ts < seg_down_start_ts and seg_down_end_ts < seg_up_end_ts:
        #    pass
        return new_start_ts