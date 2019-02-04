# Analyze market data, and track trend(s) using a state representation
from trader.lib.LargestPriceChange import LargestPriceChange


class TrendStateTrack(object):
    def __init__(self):
        self.state = None
        self.state_prev_list = []
        self.lpc = LargestPriceChange()

    def update(self, close, ts, volume=0, low=0, high=0):
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


class TrendState(object):
    STATE_UNKNOWN = 0
    STATE_INIT = 1
    STATE_NON_TREND_UP_SLOW = 2
    STATE_NON_TREND_DN_SLOW = 3
    STATE_TRENDING_UP_SLOW = 4
    STATE_TRENDING_DN_SLOW = 5
    STATE_TRENDING_UP_FAST = 6
    STATE_TRENDING_DN_FAST = 7

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

    def set_state(self, state):
        self.prev_state = self.state
        self.state = state
