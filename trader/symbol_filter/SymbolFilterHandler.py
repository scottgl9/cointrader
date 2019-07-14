
class SymbolFilterHandler(object):
    def __init__(self, accnt=None, config=None, hkdb=None):
        self.accnt = accnt
        self.config = config
        self.hkdb = hkdb
        self.filters = []

    def add_filter(self, filter_name):
        filter = None
        if filter_name == 'filter_min_usdt_value':
            from .filter.filter_min_usdt_value import filter_min_usdt_value
            filter = filter_min_usdt_value(self.accnt, self.config, self.hkdb)
        elif filter_name == 'filter_delta_ts_rank':
            from .filter.filter_delta_ts_rank import filter_delta_ts_rank
            filter = filter_delta_ts_rank(self.accnt, self.config, self.hkdb)

        if filter:
            self.filters.append(filter)
            print("Loaded filter {}".format(filter_name))
            return True
        return False

    def apply_filters(self, kline, asset_info=None):
        result = False
        if not len(self.filters):
            return result
        for filter in self.filters:
            if filter.apply_filter(kline, asset_info):
                result = True
                break
        return result
