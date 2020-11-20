# base account class for handling account information
from trader.lib.struct.Exchange import Exchange


class AccountBaseInfo(object):
    def make_ticker_id(self, base, currency):
        raise NotImplementedError

    def split_ticker_id(self, symbol):
        raise NotImplementedError

    def get_trader_mode(self):
        raise NotImplementedError

    def set_trader_mode(self, trader_mode):
        raise NotImplementedError

    def get_account_mode(self):
        raise NotImplementedError

    def set_account_mode(self, account_mode):
        raise NotImplementedError

    # fractional trade fee
    def get_trade_fee(self):
        raise NotImplementedError

    def get_currencies(self):
        raise NotImplementedError

    def get_currency_trade_pairs(self):
        raise NotImplementedError

    def get_info_all_pairs(self):
        raise NotImplementedError

    def get_info_all_assets(self):
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

    def is_currency_pair(self, symbol=None, base=None, currency=None):
        if not base or not currency:
            base, currency = self.split_ticker_id(symbol)
        if not base or not currency:
            return False
        if base not in self.get_currencies():
            return False
        if currency not in self.get_currencies():
            return False
        return True

    # return asset info in AssetInfo class object
    def get_asset_info(self, symbol=None, base=None, currency=None):
        raise NotImplementedError

    def get_asset_status(self, name=None):
        raise NotImplementedError

    def is_asset_available(self, name):
        raise NotImplementedError

    def get_asset_info_dict(self, symbol=None, base=None, currency=None, field=None):
        raise NotImplementedError
