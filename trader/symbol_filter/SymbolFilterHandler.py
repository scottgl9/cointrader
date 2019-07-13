
class SymbolFilterHandler(object):
    def __init__(self, accnt=None, config=None, hkdb=None):
        self.accnt = accnt
        self.config = config
        self.hkdb = hkdb
        self.filters = []

    def add_filter(self, filter_name):
        if filter_name == 'filter_min_usdt_value':
            from .filter.filter_min_usdt_value import filter_min_usdt_value
            filter = filter_min_usdt_value(self.accnt, self.hkdb)
            self.filters.append(filter)
            return True
        return False
