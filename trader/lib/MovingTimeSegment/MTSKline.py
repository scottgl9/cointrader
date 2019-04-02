from trader.lib.MovingTimeSegment.MTSCircularArray import MTSCircularArray
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.Kline import Kline

class MTSKline(object):
    def __init__(self, win_size_secs=60):
        self.win_size_secs = win_size_secs
        #self.mts_array = MTSCircularArray(win_secs=self.win_size_secs,
        #                                  max_win_size=(self.win_size_secs * 3) / 2,
        #                                  minmax=True)
        self.mts_array = MovingTimeSegment(self.win_size_secs, disable_fmm=False)
        self.kline = Kline()

    def ready(self):
        return self.mts_array.ready()

    def update(self, close, ts):
        self.mts_array.update(close, ts)

        if not self.mts_array.ready():
            return None

        self.kline.open = self.mts_array.first_value()
        self.kline.close = self.mts_array.last_value()
        self.kline.high = self.mts_array.max()
        self.kline.low = self.mts_array.min()
        self.kline.ts = ts

        return self.kline
