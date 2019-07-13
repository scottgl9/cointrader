from .symbol_filter_base import symbol_filter_base


class filter_min_usdt_value(symbol_filter_base):
    def __init__(self, accnt=None, hkdb=None):
        super(filter_min_usdt_value, self).__init__(accnt, hkdb)
        self.name = "filter_min_usdt_value"

    # return True if filter is applied, False if not applied
    def apply_filter(self, kline, asset_info=None):
        pass
