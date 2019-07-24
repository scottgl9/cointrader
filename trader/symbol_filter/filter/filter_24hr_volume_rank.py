# rank symbols by volume over a 24 hour period
from .symbol_filter_base import symbol_filter_base
from trader.lib.MovingTimeSegment.MTS_SMA import MTS_SMA


class filter_24hr_volume_rank(symbol_filter_base):
    def __init__(self, accnt=None, config=None, hkdb=None, logger=None):
        super(filter_24hr_volume_rank, self).__init__(accnt, config, hkdb, logger)
        self.name = "filter_24hr_volume_rank"
        self.hourly_volumes_by_symbol = {}

    #def get_sorted_avg_symbols(self, ts=0):
    #    self.sorted_avg_symbols = sorted((value, key) for (key, value) in self.avg_delta_ts_symbol.items())
    #    return self.sorted_avg_symbols

    # return True if filter is applied, False if not applied
    def apply_filter(self, kline, asset_info=None):
        result = True
        if self.hkdb and self.accnt.hourly_symbols_only() and kline.symbol not in self.hkdb.table_symbols:
            return result

        end_ts = self.accnt.get_hourly_ts(kline.ts)
        start_ts = end_ts - int(self.accnt.hours_to_ts(24))
        volumes = self.hkdb.get_kline_values_by_column(kline.symbol, column='quote_volume',
                                                       start_ts=start_ts, end_ts=end_ts)
        self.hourly_volumes_by_symbol[kline.symbol] = volumes

        return result
