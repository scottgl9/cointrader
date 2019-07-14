# rank symbols by time between realtime price updates
from .symbol_filter_base import symbol_filter_base
from trader.lib.MovingTimeSegment.MTS_SMA import MTS_SMA


class filter_delta_ts_rank(symbol_filter_base):
    def __init__(self, accnt=None, config=None, hkdb=None):
        super(filter_delta_ts_rank, self).__init__(accnt, config, hkdb)
        self.name = "filter_delta_ts_rank"
        self.prev_ts_symbol = {}
        self.mts_sma_symbol = {}
        self.avg_delta_ts_symbol = {}

    # return True if filter is applied, False if not applied
    def apply_filter(self, kline, asset_info=None):
        result = False
        try:
            prev_ts = self.prev_ts_symbol[kline.symbol]
        except KeyError:
            self.prev_ts_symbol[kline.symbol] = kline.ts
            return result

        delta_ts = kline.ts - prev_ts
        try:
            mts_sma = self.mts_sma_symbol[kline.symbol]
        except KeyError:
            mts_sma = MTS_SMA(seconds=3600)
            self.mts_sma_symbol[kline.symbol] = mts_sma

        mts_sma.update(delta_ts, kline.ts)
        if mts_sma.ready():
            self.avg_delta_ts_symbol[kline.symbol] = mts_sma.result

        self.prev_ts_symbol[kline.symbol] = kline.ts
        return result
