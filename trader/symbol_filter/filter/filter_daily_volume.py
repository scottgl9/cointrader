# rank symbols by average of time between realtime price updates
from .symbol_filter_base import symbol_filter_base
from trader.lib.hourly.DailyVolume import DailyVolume


class filter_daily_volume(symbol_filter_base):
    def __init__(self, accnt=None, config=None, hkdb=None, logger=None):
        super(filter_daily_volume, self).__init__(accnt, config, hkdb, logger)
        self.name = "filter_daily_volume"
        self.daily_volume = DailyVolume()
        self.daily_volume_btc_cutoff = float(self.config.get('daily_volume_btc_cutoff'))
        if self.logger:
            self.logger.info("Daily Volume cutoff: {}".format(self.daily_volume_btc_cutoff))

    # return True if filter is applied, False if not applied
    def apply_filter(self, kline, asset_info=None):
        if not kline.symbol.endswith('BTC'):
            return False

        self.daily_volume.update(kline.volume_quote)
        if not self.daily_volume.ready() or not self.daily_volume.result:
            return False

        if self.daily_volume.result < self.daily_volume_btc_cutoff:
            return True

        return False
