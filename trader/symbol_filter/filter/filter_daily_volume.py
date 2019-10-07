# rank symbols by average of time between realtime price updates
from .symbol_filter_base import symbol_filter_base
from trader.lib.hourly.DailyVolume import DailyVolume


class filter_daily_volume(symbol_filter_base):
    def __init__(self, accnt=None, config=None, kdb=None, logger=None):
        super(filter_daily_volume, self).__init__(accnt, config, kdb, logger)
        self.name = "filter_daily_volume"
        self.daily_volumes = {}
        self.daily_volume_btc_cutoff = float(self.config.get('daily_volume_btc_cutoff'))

        if self.logger:
            self.logger.info("Daily Volume cutoff: {}".format(self.daily_volume_btc_cutoff))

    # return True if filter is applied, False if not applied
    def apply_filter(self, kline, asset_info=None):
        if not self.kdb:
            return False

        # for now only handle BTC symbols
        if not kline.symbol.endswith('BTC'):
            return False

        if self.kdb and self.accnt.hourly_symbols_only() and kline.symbol not in self.kdb.table_symbols:
            return False

        try:
            daily_volume = self.daily_volumes[kline.symbol]
        except KeyError:
            daily_volume = DailyVolume()
            end_ts = self.accnt.get_hourly_ts(kline.ts)
            start_ts = end_ts - int(self.accnt.hours_to_ts(24 - 1))
            volumes = self.kdb.get_kline_values_by_column(kline.symbol, 'volume', start_ts, end_ts)
            for volume in volumes:
                daily_volume.update(volume)

            daily_volume.last_ts = end_ts
            self.daily_volumes[kline.symbol] = daily_volume
            return False

        if kline.ts > daily_volume.last_ts + self.accnt.hours_to_ts(1):
            hourly_ts = self.accnt.get_hourly_ts(kline.ts)
            if hourly_ts == daily_volume.last_ts:
                return False
            if not self.kdb.ts_in_table(kline.symbol, hourly_ts):
                return False

            hkline = self.kdb.get_kline(kline.symbol, hourly_ts)
            daily_volume.update(hkline.volume, ts=hkline.ts)
            self.daily_volumes[kline.symbol] = daily_volume
            if daily_volume.result < self.daily_volume_btc_cutoff:
                return True

        return False
