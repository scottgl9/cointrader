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
                       check_state_seconds=1800,
                       percent_slow_cutoff=2.0,
                       smoother=None):
        self.init_state_seconds = init_state_seconds
        self.max_state_seconds = max_state_seconds
        self.check_state_seconds = check_state_seconds
        self.percent_slow_cutoff = percent_slow_cutoff
        self.trend_state = None
        self.trend_state_prev_list = []
        self.trend_state_short = None
        self.seg_down_list = []
        self.seg_up_list = []
        self.lpc = LargestPriceChange(use_dict=True)
        self.mts_long = MovingTimeSegment(seconds=self.max_state_seconds)
        self.mts_short = MovingTimeSegment(seconds=3600)
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
        self.trend_state_short = self.process_trend_state(self.trend_state_short, self.mts_short, ts)
        self.check_start_ts = ts

    def short_state_changed(self, clear=True):
        return self.trend_state_short.state_changed(clear=clear)

    def get_short_trend_string(self):
        return self.trend_state_short.get_trend_string(self.trend_state_short.state)

    def get_short_trend_direction(self):
        return self.trend_state.direction

    def state_changed(self, clear=True):
        return self.trend_state.state_changed(clear=clear)

    def get_trend_string(self):
        return self.trend_state.get_trend_string(self.trend_state.state)

    def get_trend_direction(self):
        return self.trend_state.direction

    def reversed_direction(self, clear=True):
        return self.trend_state.reversed_direction(clear=clear)

    # process market data received from update(), and re-determine state
    def process_trend_state(self, trend_state, mts, ts):
        values = mts.get_values()
        timestamps = mts.get_timestamps()
        self.lpc.reset(values, timestamps)
        self.lpc.divide_price_segments()
        seg_down, seg_up = self.lpc.get_largest_price_segment_percents()
        trend_state = self.process_trend_segment_state(trend_state, seg_down, seg_up, ts)
        return trend_state

    def process_trend_segment_state(self, trend_state, seg_down, seg_up, ts):
        self.seg_down_list.append(seg_down)
        self.seg_up_list.append(seg_up)

        #seg_down_start_ts = seg_down['start_ts']
        #seg_up_start_ts = seg_up['start_ts']

        seg_down_percent = abs(float(seg_down['percent']))
        seg_up_percent = abs(float(seg_up['percent']))
        seg_down_end_ts = int(seg_down['end_ts'])
        seg_up_end_ts = int(seg_up['end_ts'])

        if seg_down_percent == seg_up['percent']:
            trend_state.set_state(TrendState.STATE_NON_TREND_NO_DIRECTION)
            return trend_state

        direction = 0
        # determine which direction update is most recent
        if seg_down_end_ts > seg_up_end_ts:
            direction = -1
            if trend_state.is_state(TrendState.STATE_INIT):
                trend_state.set_state(TrendState.STATE_NON_TREND_DOWN_SLOW)
        elif seg_up_end_ts > seg_down_end_ts:
            direction = 1
            if trend_state.is_state(TrendState.STATE_INIT):
                trend_state.set_state(TrendState.STATE_NON_TREND_UP_SLOW)
        else:
            trend_state.set_state(TrendState.STATE_NON_TREND_NO_DIRECTION)
            return trend_state

        # handle non-trend states
        if trend_state.is_state(TrendState.STATE_NON_TREND_NO_DIRECTION):
            # if no determined trend direction, determine non-trend direction
            if direction == -1 and seg_down_percent > seg_up_percent:
                trend_state.set_direction(direction)
                if seg_down_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_NON_TREND_DOWN_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_NON_TREND_DOWN_FAST)
            elif direction == 1 and seg_down_percent < seg_up_percent:
                trend_state.set_direction(direction)
                if seg_up_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_NON_TREND_UP_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_NON_TREND_UP_FAST)
        elif trend_state.is_state(TrendState.STATE_NON_TREND_DOWN_SLOW):
            # if determined non-trend down direction slow, determine trend direction
            if direction == -1 and seg_down_percent > seg_up_percent:
                trend_state.set_direction(direction)
                if seg_down_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_TRENDING_DOWN_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_TRENDING_DOWN_FAST)
            elif direction == 1 and seg_down_percent < seg_up_percent:
                trend_state.set_direction(direction)
                if seg_up_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_NON_TREND_UP_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_NON_TREND_UP_FAST)
        elif trend_state.is_state(TrendState.STATE_NON_TREND_UP_SLOW):
            # if determined non-trend up direction slow, determine trend direction
            if direction == -1 and seg_down_percent > seg_up_percent:
                trend_state.set_direction(direction)
                if seg_down_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_NON_TREND_DOWN_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_NON_TREND_DOWN_FAST)
            elif direction == 1 and seg_down_percent < seg_up_percent:
                trend_state.set_direction(direction)
                if seg_up_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_TRENDING_UP_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_TRENDING_UP_FAST)
        elif trend_state.is_state(TrendState.STATE_NON_TREND_DOWN_FAST):
            # if determined non-trend down direction fast, determine trend direction
            if direction == -1 and seg_down_percent > seg_up_percent:
                trend_state.set_direction(direction)
                if seg_down_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_TRENDING_DOWN_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_TRENDING_DOWN_FAST)
            elif direction == 1 and seg_down_percent < seg_up_percent:
                trend_state.set_direction(direction)
                if seg_up_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_NON_TREND_UP_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_NON_TREND_UP_FAST)
        elif trend_state.is_state(TrendState.STATE_NON_TREND_UP_FAST):
            # if determined non-trend up direction fast, determine trend direction
            if direction == -1 and seg_down_percent > seg_up_percent:
                trend_state.set_direction(direction)
                if seg_down_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_NON_TREND_DOWN_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_NON_TREND_DOWN_FAST)
            elif direction == 1 and seg_down_percent < seg_up_percent:
                trend_state.set_direction(direction)
                if seg_up_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_TRENDING_UP_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_TRENDING_UP_FAST)

        # handle trend states
        if trend_state.is_state(TrendState.STATE_TRENDING_DOWN_SLOW):
            # if determined trend down direction slow, determine trend direction
            if direction == -1 and seg_down_percent > seg_up_percent:
                trend_state.set_direction(direction)
                if seg_down_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_TRENDING_DOWN_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_TRENDING_DOWN_FAST)
            elif direction == 1 and seg_down_percent < seg_up_percent:
                trend_state.set_direction(direction)
                if seg_up_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_NON_TREND_UP_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_NON_TREND_UP_FAST)
        elif trend_state.is_state(TrendState.STATE_TRENDING_UP_SLOW):
            # if determined trend up direction slow, determine trend direction
            if direction == -1 and seg_down_percent > seg_up_percent:
                trend_state.set_direction(direction)
                if seg_down_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_NON_TREND_DOWN_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_NON_TREND_DOWN_FAST)
            elif direction == 1 and seg_down_percent < seg_up_percent:
                trend_state.set_direction(direction)
                if seg_up_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_TRENDING_UP_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_TRENDING_UP_FAST)
        elif trend_state.is_state(TrendState.STATE_TRENDING_DOWN_FAST):
            # if determined trend down direction fast, determine trend direction
            if direction == -1 and seg_down_percent > seg_up_percent:
                trend_state.set_direction(direction)
                if seg_down_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_TRENDING_DOWN_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_TRENDING_DOWN_FAST)
            elif direction == 1 and seg_down_percent < seg_up_percent:
                trend_state.set_direction(direction)
                if seg_up_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_NON_TREND_UP_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_NON_TREND_UP_FAST)
        elif trend_state.is_state(TrendState.STATE_TRENDING_UP_FAST):
            # if determined trend up direction fast, determine trend direction
            if direction == -1 and seg_down_percent > seg_up_percent:
                trend_state.set_direction(direction)
                if seg_down_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_NON_TREND_DOWN_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_NON_TREND_DOWN_FAST)
            elif direction == 1 and seg_down_percent < seg_up_percent:
                trend_state.set_direction(direction)
                if seg_up_percent < self.percent_slow_cutoff:
                    trend_state.set_state(TrendState.STATE_TRENDING_UP_SLOW)
                else:
                    trend_state.set_state(TrendState.STATE_TRENDING_UP_FAST)

        return trend_state


class TrendState(object):
    STATE_UNKNOWN = 0
    STATE_INIT = 1
    STATE_NON_TREND_NO_DIRECTION = 2
    STATE_NON_TREND_UP_SLOW = 3
    STATE_NON_TREND_DOWN_SLOW = 4
    STATE_NON_TREND_UP_FAST = 5
    STATE_NON_TREND_DOWN_FAST = 6
    STATE_TRENDING_UP_SLOW = 7
    STATE_TRENDING_DOWN_SLOW = 8
    STATE_TRENDING_UP_FAST = 9
    STATE_TRENDING_DOWN_FAST = 10
    STATE_REVERSAL_UP = 11
    STATE_REVERSAL_DOWN = 12

    def __init__(self, state):
        self.state = state
        self.prev_state = TrendState.STATE_UNKNOWN
        self.state_change = False
        self.direction = 0
        self.prev_direction = 0
        self._reverse_direction = False
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
        elif state == TrendState.STATE_NON_TREND_UP_SLOW:
                return "STATE_NON_TREND_UP_SLOW"
        elif state == TrendState.STATE_NON_TREND_DOWN_SLOW:
                return "STATE_NON_TREND_DOWN_SLOW"
        elif state == TrendState.STATE_NON_TREND_UP_FAST:
                return "STATE_NON_TREND_UP_FAST"
        elif state == TrendState.STATE_NON_TREND_DOWN_FAST:
                return "STATE_NON_TREND_DOWN_FAST"
        elif state == TrendState.STATE_TRENDING_UP_SLOW:
                return "STATE_TRENDING_UP_SLOW"
        elif state == TrendState.STATE_TRENDING_DOWN_SLOW:
                return "STATE_TRENDING_DOWN_SLOW"
        elif state == TrendState.STATE_TRENDING_UP_FAST:
                return "STATE_TRENDING_UP_FAST"
        elif state == TrendState.STATE_TRENDING_DOWN_FAST:
                return "STATE_TRENDING_DOWN_FAST"
        elif state == TrendState.STATE_REVERSAL_UP:
                return "STATE_REVERSAL_UP"
        elif state == TrendState.STATE_REVERSAL_DOWN:
                return "STATE_REVERSAL_DOWN"

    def is_state(self, state):
        return self.state == state

    def state_changed(self, clear=True):
        state_change = self.state_change
        if clear:
            self.state_change = False
        return state_change

    def set_state(self, state):
        if state != self.state:
            self.state_change = True
        self.prev_state = self.state
        self.state = state

    def set_direction(self, direction):
        if self.direction == -1 and direction == 1:
            self._reverse_direction = True
        elif self.direction == 1 and direction == -1:
            self._reverse_direction = True
        self.prev_direction = self.direction
        self.direction = direction

    def reversed_direction(self, clear=True):
        reverse_direction = self._reverse_direction
        if clear:
            self._reverse_direction = False
        return reverse_direction

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
