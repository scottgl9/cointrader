import os
import json
from trader.account.AccountBaseInfo import AccountBaseInfo

class AccountBittrexInfo(AccountBaseInfo):
    def __init__(self, client, simulation=False, logger=None, exchange_info_file=None):
        self.client = client
        self.simulate = simulation
        self.logger = logger
        self.exchange_info_file = exchange_info_file
        self.info_all_assets = {}
        self.details_all_assets = {}
        self._exchange_pairs = None
        self.currencies = ['BTC', 'ETH', 'USDT', 'USD']
        self.currency_trade_pairs = ['BTC-ETH', 'USD-BTC', 'USD-ETH', 'USD-USDT', 'USDT-BTC', 'USDT-ETH']

    def make_ticker_id(self, base, currency):
        return '%s-%s' % (currency, base)

    def split_ticker_id(self, symbol):
        base_name = None
        currency_name = None

        parts = symbol.split('-')
        if len(parts) == 2:
            currency_name = parts[0]
            base_name = parts[1]

        return base_name, currency_name

    def get_info_all_assets(self):
        return self.info_all_assets

    def get_details_all_assets(self):
        return self.details_all_assets

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
