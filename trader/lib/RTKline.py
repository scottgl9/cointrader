# convert realtime price updates to fixed time klines (ex. 1min klines)
from trader.lib.struct.Kline import Kline
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment

class RTKline(object):
    def __init__(self, win_secs=60, symbol=None):
        self.win_secs = win_secs
        self.symbol = symbol
        self.mts = MovingTimeSegment(seconds=win_secs, disable_fmm=False, enable_volume=True)
        self.kline = None
        self.last_ts = 0

    def ready(self):
        return self.mts.ready()

    def ts_to_win_interval(self, ts):
        return int(self.last_ts / self.win_secs) * self.win_secs

    def update(self, close, ts, volume):
        self.last_ts = ts
        self.mts.update(close, ts, volume)

    def get_kline(self, reset=True):
        if not self.ready():
            return None
        open = self.mts.first_value()
        close = self.mts.last_value()
        low = self.mts.min()
        high = self.mts.max()
        volume = self.mts.get_volume_sum()
        ts = self.ts_to_win_interval(self.last_ts)
        self.kline = Kline(self.symbol, open, close, low, high, volume, volume, ts)
        if reset:
            self.mts.reset()
        return self.kline
