
class SymbolFilterHandler(object):
    def __init__(self, accnt=None, config=None, hkdb=None):
        self.accnt = accnt
        self.config = config
        self.hkdb = hkdb
        self.filters = []

    def add_filter(self, filter_name):
        if filter_name == 'filter_min_usdt_value':
            from .filter.filter_min_usdt_value import filter_min_usdt_value
            filter = filter_min_usdt_value(self.accnt, self.config, self.hkdb)
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
