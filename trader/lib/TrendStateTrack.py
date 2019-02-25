# Analyze market data, and track trend(s) using a state representation
from trader.lib.LargestPriceChange import LargestPriceChange
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
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
            self.trend_state = TrendState(state=TrendState.STATE_INIT)
            self.trend_state.start_ts = ts
            self.trend_state.start_price = close
            self.trend_state.start_volume = volume
        else:
            self.trend_state.cur_ts = ts
            self.trend_state.cur_price = close
            self.trend_state.cur_volume = volume

        if not self.trend_state_short:
            self.trend_state_short = TrendState(state=TrendState.STATE_INIT)

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
                return TrendState.DIR_UP_VERY_SLOW
            elif percent < self.percent_slow_cutoff:
                return TrendState.DIR_UP_SLOW
            else:
                return TrendState.DIR_UP_FAST
        elif direction == -1:
            if percent < self.percent_very_slow_cutoff:
                return TrendState.DIR_DOWN_VERY_SLOW
            elif percent < self.percent_slow_cutoff:
                return TrendState.DIR_DOWN_SLOW
            else:
                return TrendState.DIR_DOWN_FAST
        return TrendState.DIR_NONE_NONE

    # process market data received from update(), apply LargestPriceChange algorithm, then re-determine state
    def process_trend_state(self, trend_state, mts, ts):
        values = mts.get_values()
        timestamps = mts.get_timestamps()
        self.lpc.reset(values, timestamps)
        self.lpc.divide_price_segments()
        seg_down, seg_up = self.lpc.get_largest_price_segment_percents()
        new_start_ts = self.process_lpc_result(timestamps, seg_down, seg_up)
        #if new_start_ts:
        #    mts.remove_before_ts(new_start_ts)
        #    values = mts.get_values()
        #    timestamps = mts.get_timestamps()
        #    self.lpc.reset(values, timestamps)
        #    self.lpc.divide_price_segments()
        #    seg_down, seg_up = self.lpc.get_largest_price_segment_percents()

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
            trend_state.set_state(TrendState.STATE_NON_TREND_NO_DIRECTION)
            return trend_state

        # determine which direction update is most recent
        direction = self.process_trend_direction(trend_state, seg_down, seg_up)

        if not direction:
            trend_state.set_state(TrendState.STATE_NON_TREND_NO_DIRECTION)
            return trend_state

        if trend_state.is_state(TrendState.STATE_INIT):
            if direction == 1:
                dir = self.get_direction_speed_movement(seg_up_percent, 1)
                new_state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, dir)
                trend_state.set_state(new_state)
            elif direction == -1:
                dir = self.get_direction_speed_movement(seg_down_percent, -1)
                new_state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, dir)
                trend_state.set_state(new_state)

        if trend_state.is_state(TrendState.STATE_NON_TREND_NO_DIRECTION):
            trend_state = self.process_state_non_trend_no_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_NON_TREND_DOWN_VERY_SLOW):
            trend_state = self.process_state_non_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_NON_TREND_DOWN_SLOW):
            trend_state = self.process_state_non_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_NON_TREND_DOWN_FAST):
            trend_state = self.process_state_non_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_NON_TREND_UP_VERY_SLOW):
            trend_state = self.process_state_non_trend_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_NON_TREND_UP_SLOW):
            trend_state = self.process_state_non_trend_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_NON_TREND_UP_FAST):
            trend_state = self.process_state_non_trend_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_TRENDING_DOWN_VERY_SLOW):
            trend_state = self.process_state_trending_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_TRENDING_DOWN_SLOW):
            trend_state = self.process_state_trending_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_TRENDING_DOWN_FAST):
            trend_state = self.process_state_trending_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_TRENDING_UP_VERY_SLOW):
            trend_state = self.process_state_trending_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_TRENDING_UP_SLOW):
            trend_state = self.process_state_trending_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_TRENDING_UP_FAST):
            trend_state = self.process_state_trending_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_CONT_TREND_DOWN_VERY_SLOW):
            trend_state = self.process_state_cont_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_CONT_TREND_DOWN_SLOW):
            trend_state = self.process_state_cont_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_CONT_TREND_DOWN_FAST):
            trend_state = self.process_state_cont_trend_down_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_CONT_TREND_UP_VERY_SLOW):
            trend_state = self.process_state_cont_trend_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_CONT_TREND_UP_SLOW):
            trend_state = self.process_state_cont_trend_up_direction(trend_state, seg_down, seg_up, direction)
        elif trend_state.is_state(TrendState.STATE_CONT_TREND_UP_FAST):
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
            if trend_state.get_trend_direction() != 1:
                return trend_state
        else:
            return trend_state

        type = trend_state.get_type_from_trend_state(trend_state.state)

        if type == TrendState.TYPE_CONT_TREND:
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            new_state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_TRENDING, dir)
            trend_state.set_state(new_state)
        elif type == TrendState.TYPE_TRENDING:
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            new_state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, dir)
            trend_state.set_state(new_state)
        elif type == TrendState.TYPE_NON_TREND:
            newdir = self.get_direction_speed_movement(seg_down_percent, -1)
            new_state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, newdir)
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
            if trend_state.get_trend_direction() != -1:
                return trend_state
        else:
            return trend_state

        type = trend_state.get_type_from_trend_state(trend_state.state)

        if type == TrendState.TYPE_CONT_TREND:
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            new_state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_TRENDING, dir)
            trend_state.set_state(new_state)
        elif type == TrendState.TYPE_TRENDING:
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            new_state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, dir)
            trend_state.set_state(new_state)
        elif type == TrendState.TYPE_NON_TREND:
            newdir = self.get_direction_speed_movement(seg_up_percent, 1)
            new_state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, newdir)
            trend_state.set_state(new_state)

        return trend_state

    def process_state_non_trend_no_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        return trend_state

    def process_state_non_trend_up_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_TRENDING, dir)
            trend_state.set_state(state)
        return trend_state

    def process_state_non_trend_down_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_TRENDING, dir)
            trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        return trend_state

    def process_state_trending_up_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_CONT_TREND, dir)
            trend_state.set_state(state)
        return trend_state

    def process_state_trending_down_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_CONT_TREND, dir)
            trend_state.set_state(state)
        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_NON_TREND, dir)
            trend_state.set_state(state)
        return trend_state

    def process_state_cont_trend_up_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # possible that trend is about to switch direction, so set to trend up slow
            trend_state.set_state(TrendState.STATE_TRENDING_UP_VERY_SLOW)

        elif direction == 1 and seg_down_percent < seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_up_percent, 1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_CONT_TREND, dir)
            trend_state.set_state(state)

        return trend_state

    def process_state_cont_trend_down_direction(self, trend_state, seg_down, seg_up, direction):
        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))

        if direction == -1 and seg_down_percent > seg_up_percent:
            # trend_state.set_direction(direction)
            dir = self.get_direction_speed_movement(seg_down_percent, -1)
            state = trend_state.get_trend_state_from_type_and_direction(TrendState.TYPE_CONT_TREND, dir)
            trend_state.set_state(state)

        elif direction == 1 and seg_down_percent < seg_up_percent:
            # possible that trend is about to switch direction, so set to trend down slow
            trend_state.set_state(TrendState.STATE_TRENDING_DOWN_VERY_SLOW)
        return trend_state


class TrendState(object):
    STATE_UNKNOWN                   = 0
    STATE_INIT                      = 1
    STATE_NON_TREND_NO_DIRECTION    = 2
    STATE_NON_TREND_UP_VERY_SLOW    = 3
    STATE_NON_TREND_UP_SLOW         = 4
    STATE_NON_TREND_UP_FAST         = 5
    STATE_NON_TREND_DOWN_VERY_SLOW  = 6
    STATE_NON_TREND_DOWN_SLOW       = 7
    STATE_NON_TREND_DOWN_FAST       = 8
    STATE_TRENDING_UP_VERY_SLOW     = 9
    STATE_TRENDING_UP_SLOW          = 10
    STATE_TRENDING_UP_FAST          = 11
    STATE_TRENDING_DOWN_VERY_SLOW   = 12
    STATE_TRENDING_DOWN_SLOW        = 13
    STATE_TRENDING_DOWN_FAST        = 14
    STATE_CONT_TREND_UP_VERY_SLOW   = 15
    STATE_CONT_TREND_UP_SLOW        = 16
    STATE_CONT_TREND_UP_FAST        = 17
    STATE_CONT_TREND_DOWN_VERY_SLOW = 18
    STATE_CONT_TREND_DOWN_SLOW      = 19
    STATE_CONT_TREND_DOWN_FAST      = 20
    # trend classification
    TYPE_NON_TREND                  = 21
    TYPE_TRENDING                   = 22
    TYPE_CONT_TREND                 = 23
    # direction and speed classification
    DIR_NONE_NONE                   = 24
    DIR_UP_VERY_SLOW                = 25
    DIR_UP_SLOW                     = 26
    DIR_UP_FAST                     = 27
    DIR_DOWN_VERY_SLOW              = 28
    DIR_DOWN_SLOW                   = 29
    DIR_DOWN_FAST                   = 30

    def __init__(self, state):
        self.state = state
        self.prev_state = TrendState.STATE_UNKNOWN
        self.state_change = False
        self.direction = 0
        self.prev_direction = 0
        self.direction_count = 0
        self.prev_direction_count = 0
        self.direction_speed = TrendState.DIR_NONE_NONE
        self.prev_direction_speed = TrendState.DIR_NONE_NONE
        self.direction_speed_count = 0
        self.prev_direction_speed_count = 0
        self.start_ts = 0
        self.cur_ts = 0
        self.end_ts = 0
        self.start_price = 0
        self.cur_price = 0
        self.end_price = 0
        self.start_volume = 0
        self.cur_volume = 0
        self.end_volume = 0
        self.child_state_list = None

    def get_trend_string(self, state):
        if state == TrendState.STATE_UNKNOWN:
                return "STATE_UNKNOWN"
        elif state == TrendState.STATE_INIT:
                return "STATE_INIT"
        elif state == TrendState.STATE_NON_TREND_NO_DIRECTION:
                return "STATE_NON_TREND_NO_DIRECTION"
        elif state == TrendState.STATE_NON_TREND_UP_VERY_SLOW:
                return "STATE_NON_TREND_UP_VERY_SLOW"
        elif state == TrendState.STATE_NON_TREND_UP_SLOW:
                return "STATE_NON_TREND_UP_SLOW"
        elif state == TrendState.STATE_NON_TREND_UP_FAST:
                return "STATE_NON_TREND_UP_FAST"
        elif state == TrendState.STATE_NON_TREND_DOWN_VERY_SLOW:
                return "STATE_NON_TREND_DOWN_VERY_SLOW"
        elif state == TrendState.STATE_NON_TREND_DOWN_SLOW:
                return "STATE_NON_TREND_DOWN_SLOW"
        elif state == TrendState.STATE_NON_TREND_DOWN_FAST:
                return "STATE_NON_TREND_DOWN_FAST"
        elif state == TrendState.STATE_TRENDING_UP_VERY_SLOW:
                return "STATE_TRENDING_UP_VERY_SLOW"
        elif state == TrendState.STATE_TRENDING_UP_SLOW:
                return "STATE_TRENDING_UP_SLOW"
        elif state == TrendState.STATE_TRENDING_UP_FAST:
                return "STATE_TRENDING_UP_FAST"
        elif state == TrendState.STATE_TRENDING_DOWN_VERY_SLOW:
                return "STATE_TRENDING_DOWN_VERY_SLOW"
        elif state == TrendState.STATE_TRENDING_DOWN_SLOW:
                return "STATE_TRENDING_DOWN_SLOW"
        elif state == TrendState.STATE_TRENDING_DOWN_FAST:
                return "STATE_TRENDING_DOWN_FAST"
        elif state == TrendState.STATE_CONT_TREND_UP_VERY_SLOW:
                return "STATE_CONT_TREND_UP_VERY_SLOW"
        elif state == TrendState.STATE_CONT_TREND_UP_SLOW:
                return "STATE_CONT_TREND_UP_SLOW"
        elif state == TrendState.STATE_CONT_TREND_UP_FAST:
                return "STATE_CONT_TREND_UP_FAST"
        elif state == TrendState.STATE_CONT_TREND_DOWN_VERY_SLOW:
                return "STATE_CONT_TREND_DOWN_VERY_SLOW"
        elif state == TrendState.STATE_CONT_TREND_DOWN_SLOW:
                return "STATE_CONT_TREND_DOWN_SLOW"
        elif state == TrendState.STATE_CONT_TREND_DOWN_FAST:
                return "STATE_CONT_TREND_DOWN_FAST"

    def is_state(self, state):
        return self.state == state

    # encode trend state given type and direction info
    def get_trend_state_from_type_and_direction(self, type, dir):
        state = TrendState.STATE_UNKNOWN
        if dir == TrendState.DIR_NONE_NONE:
            if type == TrendState.TYPE_NON_TREND:
                state = TrendState.STATE_NON_TREND_NO_DIRECTION
        elif dir == TrendState.DIR_UP_VERY_SLOW:
            if type == TrendState.TYPE_NON_TREND:
                state = TrendState.STATE_NON_TREND_UP_VERY_SLOW
            elif type == TrendState.TYPE_TRENDING:
                state = TrendState.STATE_TRENDING_UP_VERY_SLOW
            elif type == TrendState.TYPE_CONT_TREND:
                state = TrendState.STATE_CONT_TREND_UP_VERY_SLOW
        elif dir == TrendState.DIR_UP_SLOW:
            if type == TrendState.TYPE_NON_TREND:
                state = TrendState.STATE_NON_TREND_UP_SLOW
            elif type == TrendState.TYPE_TRENDING:
                state = TrendState.STATE_TRENDING_UP_SLOW
            elif type == TrendState.TYPE_CONT_TREND:
                state = TrendState.STATE_CONT_TREND_UP_SLOW
        elif dir == TrendState.DIR_UP_FAST:
            if type == TrendState.TYPE_NON_TREND:
                state = TrendState.STATE_NON_TREND_UP_FAST
            elif type == TrendState.TYPE_TRENDING:
                state = TrendState.STATE_TRENDING_UP_FAST
            elif type == TrendState.TYPE_CONT_TREND:
                state = TrendState.STATE_CONT_TREND_UP_FAST
        elif dir == TrendState.DIR_DOWN_VERY_SLOW:
            if type == TrendState.TYPE_NON_TREND:
                state = TrendState.STATE_NON_TREND_DOWN_VERY_SLOW
            elif type == TrendState.TYPE_TRENDING:
                state = TrendState.STATE_TRENDING_DOWN_VERY_SLOW
            elif type == TrendState.TYPE_CONT_TREND:
                state = TrendState.STATE_CONT_TREND_DOWN_VERY_SLOW
        elif dir == TrendState.DIR_DOWN_SLOW:
            if type == TrendState.TYPE_NON_TREND:
                state = TrendState.STATE_NON_TREND_DOWN_SLOW
            elif type == TrendState.TYPE_TRENDING:
                state = TrendState.STATE_TRENDING_DOWN_SLOW
            elif type == TrendState.TYPE_CONT_TREND:
                state = TrendState.STATE_CONT_TREND_DOWN_SLOW
        elif dir == TrendState.DIR_DOWN_FAST:
            if type == TrendState.TYPE_NON_TREND:
                state = TrendState.STATE_NON_TREND_DOWN_FAST
            elif type == TrendState.TYPE_TRENDING:
                state = TrendState.STATE_TRENDING_DOWN_FAST
            elif type == TrendState.TYPE_CONT_TREND:
                state = TrendState.STATE_CONT_TREND_DOWN_FAST
        return state

    # decode direction speed from trend state
    def get_direction_speed_from_trend_state(self, state):
        dir = 0
        if (state == TrendState.STATE_NON_TREND_UP_VERY_SLOW or
            state == TrendState.STATE_TRENDING_UP_VERY_SLOW or
            state == TrendState.STATE_CONT_TREND_UP_VERY_SLOW):
            dir = TrendState.DIR_UP_VERY_SLOW
        elif (state == TrendState.STATE_NON_TREND_UP_SLOW or
            state == TrendState.STATE_TRENDING_UP_SLOW or
            state == TrendState.STATE_CONT_TREND_UP_SLOW):
            dir = TrendState.DIR_UP_SLOW
        elif (state == TrendState.STATE_NON_TREND_UP_FAST or
            state == TrendState.STATE_TRENDING_UP_FAST or
            state == TrendState.STATE_CONT_TREND_UP_FAST):
            dir = TrendState.DIR_UP_SLOW
        if (state == TrendState.STATE_NON_TREND_DOWN_VERY_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_VERY_SLOW or
            state == TrendState.STATE_CONT_TREND_DOWN_VERY_SLOW):
            dir = TrendState.DIR_DOWN_VERY_SLOW
        elif (state == TrendState.STATE_NON_TREND_DOWN_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_SLOW or
            state == TrendState.STATE_CONT_TREND_DOWN_SLOW):
            dir = TrendState.DIR_DOWN_SLOW
        elif (state == TrendState.STATE_NON_TREND_DOWN_FAST or
            state == TrendState.STATE_TRENDING_DOWN_FAST or
            state == TrendState.STATE_CONT_TREND_DOWN_FAST):
            dir = TrendState.DIR_DOWN_FAST
        return dir

    # decode type from trend state
    def get_type_from_trend_state(self, state):
        type = 0
        if (state == TrendState.STATE_NON_TREND_NO_DIRECTION or
            state == TrendState.STATE_NON_TREND_UP_VERY_SLOW or
            state == TrendState.STATE_NON_TREND_UP_SLOW or
            state == TrendState.STATE_NON_TREND_UP_FAST or
            state == TrendState.STATE_NON_TREND_DOWN_VERY_SLOW or
            state == TrendState.STATE_NON_TREND_DOWN_SLOW or
            state == TrendState.STATE_NON_TREND_DOWN_FAST):
            type = TrendState.TYPE_NON_TREND
        elif (state == TrendState.STATE_TRENDING_UP_VERY_SLOW or
            state == TrendState.STATE_TRENDING_UP_SLOW or
            state == TrendState.STATE_TRENDING_UP_FAST or
            state == TrendState.STATE_TRENDING_DOWN_VERY_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_FAST):
            type = TrendState.TYPE_TRENDING
        elif (state == TrendState.STATE_CONT_TREND_UP_VERY_SLOW or
            state == TrendState.STATE_CONT_TREND_UP_SLOW or
            state == TrendState.STATE_CONT_TREND_UP_FAST or
            state == TrendState.STATE_CONT_TREND_DOWN_VERY_SLOW or
            state == TrendState.STATE_CONT_TREND_DOWN_SLOW or
            state == TrendState.STATE_CONT_TREND_DOWN_FAST):
            type = TrendState.TYPE_CONT_TREND
        return type

    # return true if is in trend state
    def is_in_trend_state(self, state=STATE_UNKNOWN):
        if state == TrendState.STATE_UNKNOWN:
            state = self.state
        if (state == TrendState.STATE_TRENDING_DOWN_VERY_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_FAST or
            state == TrendState.STATE_TRENDING_UP_VERY_SLOW or
            state == TrendState.STATE_TRENDING_UP_SLOW or
            state == TrendState.STATE_TRENDING_UP_FAST):
            return True
        elif (state == TrendState.STATE_CONT_TREND_DOWN_VERY_SLOW or
            state == TrendState.STATE_CONT_TREND_DOWN_SLOW or
            state == TrendState.STATE_CONT_TREND_DOWN_FAST or
            state == TrendState.STATE_CONT_TREND_UP_VERY_SLOW or
            state == TrendState.STATE_CONT_TREND_UP_SLOW or
            state == TrendState.STATE_CONT_TREND_UP_FAST):
            return True
        return False

    def get_trend_direction(self, state=STATE_UNKNOWN):
        direction = 0
        if state == TrendState.STATE_UNKNOWN:
            state = self.state
        if (state == TrendState.STATE_TRENDING_DOWN_VERY_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_FAST):
            direction = -1
        elif (state == TrendState.STATE_TRENDING_UP_VERY_SLOW or
             state == TrendState.STATE_TRENDING_UP_SLOW or
             state == TrendState.STATE_TRENDING_UP_FAST):
            direction = 1
        elif (state == TrendState.STATE_CONT_TREND_DOWN_VERY_SLOW or
            state == TrendState.STATE_CONT_TREND_DOWN_SLOW or
            state == TrendState.STATE_CONT_TREND_DOWN_FAST):
            direction = -1
        elif (state == TrendState.STATE_CONT_TREND_UP_VERY_SLOW or
             state == TrendState.STATE_CONT_TREND_UP_SLOW or
             state == TrendState.STATE_CONT_TREND_UP_FAST):
            direction = 1
        return direction

    def has_state_changed(self):
        return self.state != self.prev_state

    def has_direction_speed_changed(self):
        return self.direction_speed != self.prev_direction_speed

    def has_direction_speed_count_changed(self):
        return self.direction_speed_count != self.prev_direction_speed_count

    def has_direction_changed(self):
        return self.direction != self.prev_direction

    def has_direction_count_changed(self):
        return self.direction_count != self.prev_direction_count

    # conditional set state
    def set_state_conditional(self, cond, cond_true_state, cond_false_state):
        if cond:
            self.set_state(cond_true_state)
        else:
            self.set_state(cond_false_state)

    def set_state(self, state):
        # update direction from state
        direction = self.get_trend_direction(state)
        self.set_direction(direction)
        self.set_direction_speed_from_state(state)
        # update state
        self.prev_state = self.state
        self.state = state

    def set_direction_speed_from_state(self, state):
        dir = self.get_direction_speed_from_trend_state(state)
        self.prev_direction_speed = self.direction_speed
        self.direction_speed = dir
        self.prev_direction_speed_count = self.direction_speed_count
        if self.direction_speed != self.prev_direction_speed:
            self.direction_speed_count = 0
        else:
            self.direction_speed_count += 1

    def set_direction(self, direction):
        self.prev_direction = self.direction
        self.direction = direction
        # determine if direction changed or not
        self.prev_direction_count = self.direction_count
        if self.direction != self.prev_direction:
            self.direction_count = 0
        else:
            self.direction_count += 0

    def add_child_trend_state(self, trend_state):
        if not self.child_state_list:
            self.child_state_list = []
        self.child_state_list.append(trend_state)

    def remove_child_trend_state(self, trend_state):
        if not self.child_state_list:
            return
        try:
            self.child_state_list.remove(trend_state)
        except ValueError:
            pass
