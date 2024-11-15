
class SymbolFilterHandler(object):
    def __init__(self, accnt=None, config=None, kdb=None, logger=None):
        self.accnt = accnt
        self.config = config
        self.kdb = kdb
        self.logger = logger
        self.filters = []

    def add_filter(self, filter_name):
        filter_type = None
        if filter_name == 'filter_min_usdt_value':
            from .filter.filter_min_usdt_value import filter_min_usdt_value
            filter_type = filter_min_usdt_value
        elif filter_name == 'filter_daily_volume':
            from .filter.filter_daily_volume import filter_daily_volume
            filter_type = filter_daily_volume
        elif filter_name == 'filter_delta_ts_rank':
            from .filter.filter_delta_ts_rank import filter_delta_ts_rank
            filter_type = filter_delta_ts_rank
        if filter_type:
            filter = filter_type(self.accnt, self.config, self.kdb, self.logger)
            self.filters.append(filter)
            if self.logger:
                self.logger.info("Loaded filter {}".format(filter_name))
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
