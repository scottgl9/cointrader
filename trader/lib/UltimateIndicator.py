# Market data from two sources:
# 1) Real-time market data
# 2) hourly klines from sqlitedb
# for realtime
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.MovingTimeSegment.MTSCrossover2 import MTSCrossover2
# for hourly
from trader.lib.Crossover2 import Crossover2
from trader.lib.struct.CircularArray import CircularArray
from trader.indicator.EMA import EMA


class UltimateIndicator(object):
    def __init__(self):
        # realtime members
        self.rt_ema1 = EMA(12, scale=24)
        self.rt_ema2 = EMA(50, scale=24)
        self.rt_ema3 = EMA(200, scale=24)
        self.rt_mts1 = MovingTimeSegment(seconds=3600, disable_fmm=False)
        self.rt_mts2 = MovingTimeSegment(seconds=3600*4, disable_fmm=False)
        self.rt_mts3 = MovingTimeSegment(seconds=3600*8, disable_fmm=False)
        # hourly members
        self.hourly_ema1 = EMA(12)
        self.hourly_ema2 = EMA(50)
        self.hourly_ema3 = EMA(200)
        self.hourly_ca1 = CircularArray(window=24, track_minmax=True)    # daily
        self.hourly_ca2 = CircularArray(window=24*7, track_minmax=True)  # weekly
        self.hourly_ca3 = CircularArray(window=24*30, track_minmax=True) # monthly

    def update_hourly(self, ts):
        #self.hourly_ema1.update()
        pass

    def update_rt(self, close, ts, volume=0):
        self.rt_ema1.update(close, ts)
        self.rt_ema2.update(close, ts)
        self.rt_ema3.update(close, ts)
        self.rt_mts1.update(self.rt_ema1.result, ts)
        self.rt_mts2.update(self.rt_ema1.result, ts)
        self.rt_mts3.update(self.rt_ema1.result, ts)
