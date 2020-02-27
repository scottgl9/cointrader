# base account class for handling account information

class AccountBaseInfo(object):
    def make_ticker_id(self, base, currency):
        raise NotImplementedError

    def split_ticker_id(self, symbol):
        raise NotImplementedError

    def get_currencies(self):
        raise NotImplementedError

    def get_currency_trade_pairs(self):
        raise NotImplementedError

    def get_info_all_assets(self):
        raise NotImplementedError

    def get_details_all_assets(self):
        raise NotImplementedError

    def load_exchange_info(self):
        raise NotImplementedError

    def get_exchange_info(self):
        raise NotImplementedError

    def parse_exchange_info(self, pair_info, asset_info):
        raise NotImplementedError

    def get_exchange_pairs(self):
        raise NotImplementedError

    def is_exchange_pair(self, symbol):
        raise NotImplementedError

    def get_asset_status(self, name=None):
        raise NotImplementedError

    def is_asset_available(self, name):
        raise NotImplementedError

    def get_asset_info_dict(self, symbol=None, base=None, currency=None, field=None):
        raise NotImplementedError
