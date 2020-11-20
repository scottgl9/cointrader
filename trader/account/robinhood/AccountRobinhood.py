from trader.account.AccountBase import AccountBase
from trader.lib.struct.Order import Order
from trader.lib.struct.AssetInfo import AssetInfo
from trader.lib.struct.Exchange import Exchange
try:
    import trader.account.robinhood.robin_stocks as r
except ImportError:
    import robin_stocks as r
from .AccountRobinhoodInfo import AccountRobinhoodInfo
from .AccountRobinhoodBalance import AccountRobinhoodBalance
from .AccountRobinhoodTrade import AccountRobinhoodTrade
from .AccountRobinhoodMarket import AccountRobinhoodMarket
from trader.config import *
import json
import os
import time
from datetime import datetime, timedelta
import pyotp
import stix.utils.dates


class AccountRobinhood(AccountBase):
    def __init__(self, client=None, simulate=False, live=False, logger=None, simulate_db_filename=None):
        super(AccountRobinhood, self).__init__(client, simulate, live, logger, simulate_db_filename)
        self.logger = logger
        self.simulate = simulate
        self.live = live
        self.simulate_db_filename = simulate_db_filename
        if client:
            self.client = client
        elif not self.simulate:
            self.client = r
            totp = pyotp.TOTP(ROBINHOOD_2FA_KEY)
            mfa_code = totp.now()
            login = self.client.login(username=ROBINHOOD_USER, password=ROBINHOOD_PASS, mfa_code=mfa_code)

        # hourly db column names
        self.hourly_cnames = ['ts', 'low', 'high', 'open', 'close', 'volume']

        self.currencies = ['USD']
        self.currency_trade_pairs = []

        self.info = AccountRobinhoodInfo(client, simulate, logger)
        self.trade = AccountRobinhoodTrade(client, self.info, simulate, logger)
        self.market = AccountRobinhoodMarket(client, self.info, simulate, logger)
        self.balance = AccountRobinhoodBalance(client, self.info, self.market, simulate, logger)

        # keep track of initial currency buy size, and subsequent trades against currency
        self._currency_buy_size = {}
        for currency in self.currencies:
            self._currency_buy_size[currency] = 0

        self._exchange_pairs = None
        self._tickers = {}
        self._min_tickers = {}
        self._max_tickers = {}
        self._trader_profit_mode = 'USD'
        self._tpprofit = 0
        self.initial_currency = 0
        self.loaded_model_count = 0

    def ts_to_iso8601(self, ts):
        dt = datetime.fromtimestamp(ts)
        return stix.utils.dates.serialize_value(dt)

    # if hourly table name doesn't match symbol name
    # ex. symbol 'BTC-USD', db table name 'BTC_USD'
    def get_hourly_table_name(self, symbol):
        return symbol.replace('-', '_')

    # get symbol name from hourly table name
    # ex. table name 'BTC_USD', return symbol 'BTC-USD'
    def get_symbol_hourly_table(self, table_name):
        return table_name.replace('_', '-')

    # get hourly db column names
    def get_hourly_column_names(self):
        return self.hourly_cnames

    def get_ticker_id(self, symbol):
        try:
            info = self.get_info_all_pairs()[symbol]
            return info['id']
        except KeyError:
            return ''

    def set_trader_profit_mode(self, mode):
        if mode in self.currencies:
            self._trader_profit_mode = mode
        else:
            self.logger.info("set_trader_profit_mode({}) FAILED".format(mode))

    def get_trader_profit_mode(self):
        return self._trader_profit_mode

    def set_total_percent_profit(self, tpprofit):
        self._tpprofit = tpprofit

    def get_total_percent_profit(self):
        return self._tpprofit

    def get_currency_trade_pairs(self):
        return self.currency_trade_pairs

    def get_currency_buy_size(self, name):
        if not self.is_currency(name):
            return 0
        return self._currency_buy_size[name]

    def set_currency_buy_size(self, name, size=0):
        if not self.is_currency(name):
            return 0
        self._currency_buy_size[name] = size

    # buy_size is amount of currency used to buy an asset
    # sell_size is amount of currency retrieved by selling asset
    def update_currency_buy_size(self, name, asset_buy_size=0, asset_sell_size=0):
        if not self.is_currency(name):
            return 0
        if asset_buy_size:
            self._currency_buy_size[name] -= asset_buy_size
        if asset_sell_size:
            self._currency_buy_size[name] += asset_sell_size
        return self._currency_buy_size[name]
