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
        self.exchange_type = Exchange.EXCHANGE_ROBINHOOD
        self.exchange_name = Exchange.name(self.exchange_type)
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
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

        self._trader_mode = AccountBase.TRADER_MODE_NONE

        # hourly db column names
        self.hourly_cnames = ['ts', 'low', 'high', 'open', 'close', 'volume']

        self.currencies = ['USD']
        self.currency_trade_pairs = []

        self.info = AccountRobinhoodInfo(client, simulate, logger, self.exchange_info_file)
        self.balance = AccountRobinhoodBalance(client, simulate, logger)
        self.trade = AccountRobinhoodTrade(client, simulate, logger)
        self.market = AccountRobinhoodMarket(client, self.info, simulate, logger)

        # keep track of initial currency buy size, and subsequent trades against currency
        self._currency_buy_size = {}
        for currency in self.currencies:
            self._currency_buy_size[currency] = 0

        self._exchange_pairs = None
        self._tickers = {}
        self._min_tickers = {}
        self._max_tickers = {}
        self._trader_profit_mode = 'BTC'
        self._tpprofit = 0
        self.initial_currency = 0
        self.loaded_model_count = 0

    # get config section name from trader.ini
    def get_config_section_name(self):
        if self.simulate:
            name = "{}.simulate".format(self.exchange_name)
        else:
            name = "{}.live".format(self.exchange_name)
        return name

    def get_trader_mode(self):
        return self._trader_mode

    def set_trader_mode(self, trader_mode):
        self._trader_mode = trader_mode

    def trade_mode_hourly(self):
        return self._trader_mode == AccountBase.TRADER_MODE_HOURLY

    def trade_mode_realtime(self):
        return self._trader_mode == AccountBase.TRADER_MODE_REALTIME

    def ts_to_iso8601(self, ts):
        dt = datetime.fromtimestamp(ts)
        return stix.utils.dates.serialize_value(dt)

    def format_ts(self, ts):
        return int(ts)

    def ts_to_seconds(self, ts):
        return float(ts)

    # returns true if this ts is an hourly ts
    def is_hourly_ts(self, ts):
        hourly_ts = self.get_hourly_ts(ts)
        return int(ts) == hourly_ts

    # set minutes and seconds components of timestamp to zero
    def get_hourly_ts(self, ts):
        #dt = datetime.utcfromtimestamp(self.ts_to_seconds(ts)).replace(minute=0, second=0)
        #return int(self.seconds_to_ts(time.mktime(dt.timetuple())))
        return int(self.ts_to_seconds(ts) / 3600.0) * 3600

    def seconds_to_ts(self, seconds):
        return float(seconds)

    def hours_to_ts(self, hours):
        return float(hours * 3600)

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
            info = self.get_info_all_assets()[symbol]
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

    def round_base(self, price, base_increment=0):
        if base_increment:
            try:
                precision = '{:.8f}'.format(float(base_increment)).index('1')
                if float(base_increment) < 1.0:
                    precision -= 1
            except ValueError:
                self.logger.warning("round_base(): index not found in {}, price={}".format(base_increment, price))
                return price

            return round(float(price), precision)
        return price

    def round_quote(self, price, quote_increment=0):
        if quote_increment:
            try:
                precision = '{:.8f}'.format(float(quote_increment)).index('1')
                if float(quote_increment) < 1.0:
                    precision -= 1
            except ValueError:
                self.logger.warning("round_quote(): index not found in {}, price={}".format(quote_increment, price))
                return price
            return round(float(price), precision)
        return price

    def round_quantity(self, size, min_qty=0):
        if min_qty:
            try:
                precision = '{:.8f}'.format(float(min_qty)).index('1')
                if float(min_qty) < 1.0:
                    precision -= 1
            except ValueError:
                self.logger.warning("round_quantity(): index not found in {}, size={}".format(min_qty, size))
                return size
            return round(float(size), precision)
        return size

    def round_base_symbol(self, symbol, price):
        base_increment = self.get_asset_info_dict(symbol=symbol, field='base_step_size')
        return self.round_base(price, base_increment)

    def round_quantity_symbol(self, symbol, size):
        min_qty = self.get_asset_info_dict(symbol=symbol, field='min_qty')
        return self.round_quantity(size, min_qty)

    def round_quote_symbol(self, symbol, price):
        quote_increment = self.get_asset_info_dict(symbol=symbol, field='currency_step_size')
        return self.round_quote(price, quote_increment)

    def round_quote_pair(self, base, currency, price):
        quote_increment = self.get_asset_info_dict(base=base, currency=currency, field='currency_step_size')
        return self.round_quote(price, quote_increment)

    def my_float(self, value):
        if float(value) >= 0.1:
            return "{}".format(float(value))
        else:
            return "{:.8f}".format(float(value))

    def get_base_step_size(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return 0
        return info['base_step_size']

    def get_currency_step_size(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return 0
        return info['currency_step_size']

    def get_account_total_value(self, currency='USD', detailed=False):
        result = dict()
        result['assets'] = {}

        total_balance = 0.0

        for asset, value in self.get_account_balances(detailed=False).items():
            if float(value) == 0:
                continue
            if asset == currency:
                total_balance += value
                continue
            elif currency != 'USD' and asset == 'USD':
                symbol = self.make_ticker_id(currency, asset)
                price = float(self.get_ticker(symbol))
                if price:
                    total_balance += value / price
                elif self.simulate:
                    return 0.0
                continue
            symbol = self.make_ticker_id(asset, currency)
            price = float(self.get_ticker(symbol))
            if self.simulate and not price:
                return 0.0
            elif not price:
                continue
            total_balance += value * price

        return total_balance
