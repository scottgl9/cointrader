# rank symbols by volume over a 24 hour period
from .symbol_filter_base import symbol_filter_base
from trader.lib.MovingTimeSegment.MTS_SMA import MTS_SMA


class filter_24hr_volume_rank(symbol_filter_base):
    def __init__(self, accnt=None, config=None, hkdb=None, logger=None):
        super(filter_24hr_volume_rank, self).__init__(accnt, config, hkdb, logger)
        self.name = "filter_24hr_volume_rank"
        self.hourly_klines_by_symbol = {}
        self.volume_24hr_by_symbol = {}
        self.sorted_24hr_volumes = None

    def get_sorted_24hr_volumes(self):
        return sorted(((value, key) for (key, value) in self.volume_24hr_by_symbol.items()), reverse=True)

    # return True if filter is applied, False if not applied
    def apply_filter(self, kline, asset_info=None):
        result = True
        if self.hkdb and self.accnt.hourly_symbols_only() and kline.symbol not in self.hkdb.table_symbols:
            return result

        if kline.symbol.endswith('USDT'):
            return False

        try:
            klines = self.hourly_klines_by_symbol[kline.symbol]
            if kline.ts - klines[-1].ts > self.accnt.hours_to_ts(1):
                hourly_ts = self.accnt.get_hourly_ts(kline.ts)
                if self.hkdb.ts_in_table(kline.symbol, hourly_ts):
                    new_kline = self.hkdb.get_kline(kline.symbol, hourly_ts)
                    self.volume_24hr_by_symbol[kline.symbol] -= klines[0].volume_quote
                    self.volume_24hr_by_symbol[kline.symbol] += new_kline.volume_quote
                    klines.append(new_kline)
                    self.hourly_klines_by_symbol[kline.symbol] = klines[1:]
                    sorted_24hr_volumes = self.get_sorted_24hr_volumes()
                    self.sorted_24hr_volumes = dict(sorted_24hr_volumes[:len(sorted_24hr_volumes)*3/4])
        except KeyError:
            end_ts = self.accnt.get_hourly_ts(kline.ts)
            start_ts = end_ts - int(self.accnt.hours_to_ts(24 - 1))
            klines = self.hkdb.get_klines(kline.symbol, start_ts, end_ts)
            self.hourly_klines_by_symbol[kline.symbol] = klines
            volume_24hr = 0
            for k in klines:
                volume_24hr += k.volume_quote
            self.volume_24hr_by_symbol[kline.symbol] = volume_24hr

        if self.sorted_24hr_volumes and kline.symbol in self.sorted_24hr_volumes.values():
            result = False

        return result
