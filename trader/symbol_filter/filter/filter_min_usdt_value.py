from .symbol_filter_base import symbol_filter_base


class filter_min_usdt_value(symbol_filter_base):
    def __init__(self, accnt=None, config=None, hkdb=None):
        super(filter_min_usdt_value, self).__init__(accnt, config, hkdb)
        self.name = "filter_min_usdt_value"
        self.usdt_value_cutoff = float(self.config.get('usdt_value_cutoff'))
        print(self.usdt_value_cutoff)

    # return True if filter is applied, False if not applied
    def apply_filter(self, kline, asset_info=None):
        # check USDT value of base by calculating (base_currency) * (currency_usdt)
        # verify that USDT value >= self.usdt_value_cutoff, if less do not buy
        usdt_value = self.accnt.get_usdt_value_symbol(kline.symbol, float(kline.close))
        if usdt_value:
            if usdt_value < self.usdt_value_cutoff:
                return True
        return False
