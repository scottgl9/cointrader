# Analyze market data, and track trend(s) using a state representation
from trader.lib.LargestPriceChange import LargestPriceChange
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.indicator.EMA import EMA


# init_state_seconds: time allowed to capture market data before determining state
# max_state_seconds: maximum amount of time that moving data segment accumulates data
# check_state_seconds: interval at which state is check, and determine if move to new state
class TrendStateTrack(object):
    def __init__(self, init_state_seconds=(3600 * 2),
                       max_state_seconds=(3600 * 12),
                       check_state_seconds=3600):
        self.init_state_seconds = init_state_seconds
        self.max_state_seconds = max_state_seconds
        self.check_state_seconds = check_state_seconds
        self.state = None
        self.state_prev_list = []
        self.lpc = LargestPriceChange()
        self.start_ts = 0
        self.ready = False

    def update(self, close, ts, volume=0, low=0, high=0):
        if not self.start_ts:
            self.start_ts = ts
        elif not self.ready:
            if (ts - self.start_ts) > self.init_state_seconds * 1000:
                self.ready = True

        # init of state
        if not self.state:
            self.state = TrendState(state=TrendState.STATE_INIT)
            self.state.start_ts = ts
            self.state.start_price = close
            self.state.start_volume = volume
        else:
            self.state.cur_ts = ts
            self.state.cur_price = close
            self.state.cur_volume = volume

        if not self.ready:
            return


class TrendState(object):
    STATE_UNKNOWN = 0
    STATE_INIT = 1
    STATE_NON_TREND_NO_DIRECTION = 2
    STATE_NON_TREND_UP_SLOW = 3
    STATE_NON_TREND_DOWN_SLOW = 4
    STATE_TRENDING_UP_SLOW = 5
    STATE_TRENDING_DOWN_SLOW = 6
    STATE_TRENDING_UP_FAST = 7
    STATE_TRENDING_DOWN_FAST = 8
    STATE_LOCAL_PEAK = 9
    STATE_LOCAL_VALLEY = 10

    def __init__(self, state):
        self.state = state
        self.prev_state = TrendState.STATE_UNKNOWN
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

    def set_state(self, state):
        self.prev_state = self.state
        self.state = state

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
