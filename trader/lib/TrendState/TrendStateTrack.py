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
        self.seg_down_list = []
        self.seg_up_list = []
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
            self.trend_state = TrendState(state=TrendStateInfo.STATE_INIT)
            self.trend_state.start_ts = ts
            self.trend_state.start_price = close
            self.trend_state.start_volume = volume
        else:
            self.trend_state.cur_ts = ts
            self.trend_state.cur_price = close
            self.trend_state.cur_volume = volume

        if not self.trend_state_short:
            self.trend_state_short = TrendState(state=TrendStateInfo.STATE_INIT)

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
        return self.trend_state_short.get_trend_string(self.trend_state_short.state)

    def get_short_trend_direction(self):
        return self.trend_state.direction

    def has_trend_state_changed(self):
        return self.trend_state.has_state_changed()

    def is_in_trend_state(self):
        return self.trend_state.is_in_trend_state()

    def state_changed(self):
        return self.trend_state.has_state_changed()

    def get_trend_state(self):
        return self.trend_state.state

    def get_trend_string(self):
        return self.trend_state.get_trend_string(self.trend_state.state)

    def get_trend_direction(self):
        return self.trend_state.direction

    def get_direction_speed_movement(self, percent, direction):
        if direction == 1:
            if percent < self.percent_very_slow_cutoff:
                return TrendStateInfo.DIR_UP_VERY_SLOW
            elif percent < self.percent_slow_cutoff:
                return TrendStateInfo.DIR_UP_SLOW
            else:
                return TrendStateInfo.DIR_UP_FAST
        elif direction == -1:
            if percent < self.percent_very_slow_cutoff:
                return TrendStateInfo.DIR_DOWN_VERY_SLOW
            elif percent < self.percent_slow_cutoff:
                return TrendStateInfo.DIR_DOWN_SLOW
            else:
                return TrendStateInfo.DIR_DOWN_FAST
        return TrendStateInfo.DIR_NONE_NONE

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

        trend_state = self.process_trend_segment_state(trend_state, seg_down, seg_up, ts)
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

    def process_trend_segment_state(self, trend_state, seg_down, seg_up, ts):
        self.seg_down_list.append(seg_down)
        self.seg_up_list.append(seg_up)

        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if seg_down_percent == seg_up_percent:
            trend_state.set_state(TrendStateInfo.STATE_NON_TREND_NO_DIRECTION)
            return trend_state

        # determine which direction update is most recent
        direction = self.process_trend_direction(trend_state, seg_down, seg_up)

        if not direction:
            trend_state.set_state(TrendStateInfo.STATE_NON_TREND_NO_DIRECTION)
            return trend_state

        if trend_state.is_state(TrendStateInfo.STATE_INIT):
            if direction == 1:
                dir = self.get_direction_speed_movement(seg_up_percent, 1)
                new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
                trend_state.set_state(new_state)
            elif direction == -1:
                dir = self.get_direction_speed_movement(seg_down_percent, -1)
                new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
                trend_state.set_state(new_state)

        if trend_state.is_state(TrendStateInfo.STATE_NON_TREND_NO_DIRECTION):
            trend_state = self.process_state_non_trend_no_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_NON_TREND_DOWN_VERY_SLOW):
            trend_state = self.process_state_non_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_NON_TREND_DOWN_SLOW):
            trend_state = self.process_state_non_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_NON_TREND_DOWN_FAST):
            trend_state = self.process_state_non_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_NON_TREND_UP_VERY_SLOW):
            trend_state = self.process_state_non_trend_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_NON_TREND_UP_SLOW):
            trend_state = self.process_state_non_trend_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_NON_TREND_UP_FAST):
            trend_state = self.process_state_non_trend_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW):
            trend_state = self.process_state_trending_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_TRENDING_DOWN_SLOW):
            trend_state = self.process_state_trending_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_TRENDING_DOWN_FAST):
            trend_state = self.process_state_trending_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_TRENDING_UP_VERY_SLOW):
            trend_state = self.process_state_trending_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_TRENDING_UP_SLOW):
            trend_state = self.process_state_trending_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_TRENDING_UP_FAST):
            trend_state = self.process_state_trending_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_DOWN_VERY_SLOW):
            trend_state = self.process_state_cont_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_DOWN_SLOW):
            trend_state = self.process_state_cont_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_DOWN_FAST):
            trend_state = self.process_state_cont_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_UP_VERY_SLOW):
            trend_state = self.process_state_cont_trend_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_UP_SLOW):
            trend_state = self.process_state_cont_trend_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendStateInfo.STATE_CONT_TREND_UP_FAST):
            trend_state = self.process_state_cont_trend_up_direction(trend_state, seg_down, seg_up, direction)

        # check if the state hasn't changed, and trend could be changing
        if not self.has_trend_state_changed() and len(self.seg_down_list) > 2 and len(self.seg_up_list) > 2:
            trend_state = self.process_potential_upward_reversal(trend_state, seg_down, seg_up, direction)
            trend_state = self.process_potential_downward_reversal(trend_state, seg_down, seg_up, direction)

        return trend_state

    def process_trend_direction(self, trend_state, seg_down, seg_up):
        seg_down_start_ts = int(seg_down['start_ts'])
        seg_up_start_ts = int(seg_up['start_ts'])
        seg_down_end_ts = int(seg_down['end_ts'])
        seg_up_end_ts = int(seg_up['end_ts'])

        direction = 0

        # determine which direction update is most recent
        if seg_down_end_ts > seg_up_end_ts or seg_down_start_ts > seg_up_end_ts:
            direction = -1
        elif seg_up_end_ts > seg_down_end_ts or seg_up_start_ts > seg_down_end_ts:
            direction = 1

        return direction

    def process_potential_downward_reversal(self, trend_state, seg_down, seg_up, direction):
        seg_down_prev = self.seg_down_list[-2]
        seg_up_prev = self.seg_up_list[-2]
        seg_down_prev_percent = abs(float(seg_down_prev['percent']))
        seg_up_prev_percent = abs(float(seg_up_prev['percent']))
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        # check if could be downward trend reversal
        if seg_up_percent < seg_up_prev_percent and seg_down_percent > seg_down_prev_percent:
            if TrendStateInfo.get_trend_direction(trend_state.state) != 1:
                return trend_state
        else:
            return trend_state

        type = TrendStateInfo.get_type_from_trend_state(trend_state.state)

        if type == TrendStateInfo.TYPE_CONT_TREND:
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_TRENDING:
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_NON_TREND:
            newdir = self.get_direction_speed_movement(seg_down_percent, -1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, newdir)
            trend_state.set_state(new_state)

        return trend_state

    def process_potential_upward_reversal(self, trend_state, seg_down, seg_up, direction):
        seg_down_prev = self.seg_down_list[-2]
        seg_up_prev = self.seg_up_list[-2]
        seg_down_prev_percent = abs(float(seg_down_prev['percent']))
        seg_up_prev_percent = abs(float(seg_up_prev['percent']))
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        # check if could be upward trend reversal
        if seg_up_percent > seg_up_prev_percent and seg_down_percent < seg_down_prev_percent:
            if TrendStateInfo.get_trend_direction(trend_state.state) != -1:
                return trend_state
        else:
            return trend_state

        type = TrendStateInfo.get_type_from_trend_state(trend_state.state)

        if type == TrendStateInfo.TYPE_CONT_TREND:
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_TRENDING:
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            trend_state.set_state(new_state)
        elif type == TrendStateInfo.TYPE_NON_TREND:
            newdir = self.get_direction_speed_movement(seg_up_percent, 1)
            new_state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, newdir)
            trend_state.set_state(new_state)

        return trend_state

    def process_state_non_trend_no_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        return trend_state

    def process_state_non_trend_up_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            trend_state.set_state(state)
        return trend_state

    def process_state_non_trend_down_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_TRENDING, dir)
            trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        return trend_state

    def process_state_trending_up_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            trend_state.set_state(state)
        return trend_state

    def process_state_trending_down_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        return trend_state

    def process_state_cont_trend_up_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # possible that trend is about to switch direction, so set to trend up slow
            trend_state.set_state(TrendStateInfo.STATE_TRENDING_UP_VERY_SLOW)

        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            trend_state.set_state(state)

        return trend_state

    def process_state_cont_trend_down_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = TrendStateInfo.get_trend_state_from_type_and_direction(TrendStateInfo.TYPE_CONT_TREND, dir)
            trend_state.set_state(state)

        elif direction == 1 and seg_down_percent < seg_up_percent:
            # possible that trend is about to switch direction, so set to trend down slow
            trend_state.set_state(TrendStateInfo.STATE_TRENDING_DOWN_VERY_SLOW)
        return trend_state


