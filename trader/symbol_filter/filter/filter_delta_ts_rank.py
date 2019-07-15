# rank symbols by average of time between realtime price updates
from .symbol_filter_base import symbol_filter_base
from trader.lib.MovingTimeSegment.MTS_SMA import MTS_SMA


class filter_delta_ts_rank(symbol_filter_base):
    def __init__(self, accnt=None, config=None, hkdb=None, logger=None, min_table_size=10, max_secs=60):
        super(filter_delta_ts_rank, self).__init__(accnt, config, hkdb, logger)
        self.name = "filter_delta_ts_rank"
        self.prev_ts_symbol = {}
        self.mts_sma_symbol = {}
        self.avg_delta_ts_symbol = {}
        self.sorted_avg_symbols = None
        self.min_table_size = min_table_size
        # cutoff for maximum amount of seconds average between trades
        self.max_secs = max_secs

    def get_sorted_avg_symbols(self, ts=0):
        self.sorted_avg_symbols = sorted((value, key) for (key, value) in self.avg_delta_ts_symbol.items())
        return self.sorted_avg_symbols

    # return True if filter is applied, False if not applied
    def apply_filter(self, kline, asset_info=None):
        result = True
        if self.hkdb and self.accnt.hourly_symbols_only() and kline.symbol not in self.hkdb.table_symbols:
            return result

        try:
            prev_ts = self.prev_ts_symbol[kline.symbol]
        except KeyError:
            self.prev_ts_symbol[kline.symbol] = kline.ts
            return result

        delta_ts = self.accnt.ts_to_seconds(kline.ts - prev_ts)
        try:
            mts_sma = self.mts_sma_symbol[kline.symbol]
        except KeyError:
            mts_sma = MTS_SMA(seconds=3600)
            self.mts_sma_symbol[kline.symbol] = mts_sma

        mts_sma.update(delta_ts, kline.ts)
        if mts_sma.ready():
            self.avg_delta_ts_symbol[kline.symbol] = mts_sma.result
            if len(self.avg_delta_ts_symbol) > self.min_table_size:
                try:
                    avg_delta_ts = self.avg_delta_ts_symbol[kline.symbol]
                    if avg_delta_ts <= self.max_secs:
                        result = False
                except KeyError:
                    pass
                #print(self.get_sorted_avg_symbols())

        self.prev_ts_symbol[kline.symbol] = kline.ts
        return result
