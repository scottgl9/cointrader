# convert realtime price updates to fixed time klines (ex. 1min klines)
from trader.lib.struct.Kline import Kline
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment

class RTKline(object):
    def __init__(self, win_secs=300, symbol=None):
        self.win_secs = win_secs
        self.symbol = symbol
        self.mts = MovingTimeSegment(seconds=win_secs, disable_fmm=False, enable_volume=True)
        self.kline = None
        self.start_ts = 0
        self.last_ts = 0

    def ready(self):
        if self.mts.ready():
            return True
        #if self.last_ts and self.last_ts - self.start_ts >= self.win_secs * 1000:
        #    return True
        return False

    def ts_to_win_interval(self, ts):
        return int(ts / self.win_secs) * self.win_secs

    def update(self, close, ts, volume):
        if not self.start_ts:
            self.start_ts = ts
        self.last_ts = ts
        self.mts.update(close, ts, volume)

    def get_kline(self, reset=True):
        if not self.ready():
            return None
        open = self.mts.first_value()
        close = self.mts.last_value()
        low = self.mts.min()
        if low < open:
            low = open
        if low < close:
            low = close
        high = self.mts.max()
        if high > open:
            high = open
        if high > close:
            high = close
        volume = self.mts.get_volume_sum()
        ts = self.ts_to_win_interval(self.last_ts)
        self.kline = Kline(self.symbol, open, close, low, high, volume, volume, ts)
        if reset:
            self.mts.reset()
        return self.kline
