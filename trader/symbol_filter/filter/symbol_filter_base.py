class symbol_filter_base(object):
    def __init__(self, accnt=None, config=None, hkdb=None, logger=None):
        self.name = None
        self.accnt = accnt
        self.config = config
        self.hkdb = hkdb
        self.logger = logger

    # return True if filter is applied, False if not applied
    def apply_filter(self, kline, asset_info=None):
        return False