# Market data from two sources:
# 1) Real-time market data
# 2) hourly klines from sqlitedb
# for realtime
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.MovingTimeSegment.MTSCrossover3 import MTSCrossover3
# for hourly
from trader.lib.Crossover3 import Crossover3
from trader.lib.struct.CircularArray import CircularArray
from trader.indicator.EMA import EMA

class UltimateIndicator(object):
    def __init__(self, kdb=None, accnt=None, symbol=None, asset_info=None):
        self.kdb = kdb
        self.accnt = accnt
        self.symbol = symbol
        self.asset_info = asset_info
        # realtime members
        self.rt_ema1 = EMA(12, scale=24)
        self.rt_ema2 = EMA(50, scale=24)
        self.rt_ema3 = EMA(200, scale=24)
        self.rt_mts1 = MovingTimeSegment(seconds=3600, disable_fmm=False)
        self.rt_mts2 = MovingTimeSegment(seconds=3600*4, disable_fmm=False)
        self.rt_mts3 = MovingTimeSegment(seconds=3600*8, disable_fmm=False)
        self.rt_cross = MTSCrossover3(win_secs=60)
        # hourly members
        self.hourly_ema1 = EMA(12)
        self.hourly_ema2 = EMA(50)
        self.hourly_ema3 = EMA(200)
        self.hourly_ca1 = CircularArray(window=24, track_minmax=True)    # daily
        self.hourly_ca2 = CircularArray(window=24*7, track_minmax=True)  # weekly
        self.hourly_ca3 = CircularArray(window=24*30, track_minmax=True) # monthly
        self.hourly_cross = Crossover3(window=12)

    # hourly update
    def update_hourly(self, hourly_ts):
        kline = self.kdb.get_dict_kline(self.symbol, hourly_ts)

        # hourly kline not in db yet, wait until next update() call
        if not kline:
            return False

        self.hourly_ema1.update(kline.close)
        self.hourly_ema2.update(kline.close)
        self.hourly_ema3.update(kline.close)
        self.hourly_ca1.add(self.hourly_ema1.result)
        self.hourly_ca2.add(self.hourly_ema2.result)
        self.hourly_ca3.add(self.hourly_ema3.result)
        self.hourly_cross.update(self.hourly_ema1.result, self.hourly_ema2.result, self.hourly_ema3.result, kline.ts)

    # realtime update
    def update(self, close, ts, volume=0):
        self.rt_ema1.update(close, ts)
        self.rt_ema2.update(close, ts)
        self.rt_ema3.update(close, ts)
        self.rt_mts1.update(self.rt_ema1.result, ts)
        self.rt_mts2.update(self.rt_ema1.result, ts)
        self.rt_mts3.update(self.rt_ema1.result, ts)
        self.rt_cross.update(self.rt_ema1.result, self.rt_ema2.result, self.rt_ema3.result, ts)
