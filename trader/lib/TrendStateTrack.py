# Analyze market data, and track trend(s) using a state representation


class TrendStateTrack(object):
    STATE_UNKNOWN = 0
    STATE_INIT = 1
    STATE_NON_TRENDING = 2
    STATE_TRENDING_UP_SLOW = 3
    STATE_TRENDING_DN_SLOW = 4
    STATE_TRENDING_UP_FAST = 5
    STATE_TRENDING_DN_FAST = 6

    def __init__(self):
        self.state = self.STATE_INIT

    def update(self, close, ts, low=0, high=0, volume=0):
        pass
