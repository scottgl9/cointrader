from trader.account.bittrex.bittrex import Bittrex, API_V2_0
from trader.account.AccountBase import AccountBase
from .AccountBittrexInfo import AccountBittrexInfo
from .AccountBittrexBalance import AccountBittrexBalance
from .AccountBittrexTrade import AccountBittrexTrade
from .AccountBittrexMarket import AccountBittrexMarket
from trader.lib.struct.TraderMessage import TraderMessage
from trader.lib.struct.Order import Order
from trader.lib.struct.OrderUpdate import OrderUpdate
from trader.lib.struct.AssetInfo import AssetInfo
from trader.lib.struct.Exchange import Exchange
from trader.config import *

import json
import os


#logger = logging.getLogger(__name__)

class AccountBittrex(AccountBase):
    def __init__(self, client=None, simulate=False, live=False, logger=None, simulate_db_filename=None):
        super(AccountBittrex, self).__init__(client, simulate, live, logger, simulate_db_filename)
        self.exchange_type = Exchange.EXCHANGE_BITTREX
        self.exchange_name = Exchange.name(self.exchange_type)
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.logger = logger
        self.simulate_db_filename = simulate_db_filename
        if client:
            self.client = client
        else:
            self.client = Bittrex(api_key=BITTREX_API_KEY, api_secret=BITTREX_API_SECRET, api_version=API_V2_0)
        self.simulate = simulate
        self.live = live
        self.info_all_pairs = {}
        self.info_all_assets = {}
        self.balances = {}

        # sub module implementations
        self.info = AccountBittrexInfo(client, simulate, logger)
        self.trade = AccountBittrexTrade(client, self.info, simulate, logger)
        self.market = AccountBittrexMarket(client, self.info, simulate, logger)
        self.balance = AccountBittrexBalance(client, self.info, self.market, simulate, logger)

        # keep track of initial currency buy size, and subsequent trades against currency
        self._currency_buy_size = {}
        for currency in self.info.get_currencies():
            self._currency_buy_size[currency] = 0

        self.client = client

        self._trader_profit_mode = 'BTC'
        self._tpprofit = 0
        self.initial_currency = 0
        self._max_market_buy = 0
        self.loaded_model_count = 0

    # get config section name from trader.ini
    def get_config_section_name(self):
        if self.simulate:
            name = "{}.simulate".format(self.exchange_name)
        else:
            name = "{}.live".format(self.exchange_name)
        return name

    # def format_ts(self, ts):
    #     return int(ts)
    #
    # def ts_to_seconds(self, ts):
    #     return float(ts / 1000.0)
    #
    # # returns true if this ts is an hourly ts
    # def is_hourly_ts(self, ts):
    #     hourly_ts = self.get_hourly_ts(ts)
    #     return int(ts) == hourly_ts
    #
    # # set minutes and seconds components of timestamp to zero
    # def get_hourly_ts(self, ts):
    #     #dt = datetime.utcfromtimestamp(self.ts_to_seconds(ts)).replace(minute=0, second=0)
    #     #return int(self.seconds_to_ts(time.mktime(dt.timetuple())))
    #     return int(self.ts_to_seconds(ts) / 3600.0) * 3600 * 1000
    #
    # def seconds_to_ts(self, seconds):
    #     return float(seconds * 1000)
    #
    # def hours_to_ts(self, hours):
    #     return float(hours * 3600 * 1000)

    # if hourly table name doesn't match symbol name
    # ex. symbol 'BTC-USD', table name 'BTC_USD'
    def get_hourly_table_name(self, symbol):
        return symbol

    # get symbol name from hourly table name
    # ex. table name 'BTC_USD', return symbol 'BTC-USD'
    def get_symbol_hourly_table(self, table_name):
        return table_name

    def set_trader_profit_mode(self, mode):
        if mode in self.info.get_currencies():
            self._trader_profit_mode = mode
        else:
            self.logger.info("set_trader_profit_mode({}) FAILED".format(mode))

    def get_trader_profit_mode(self):
        return self._trader_profit_mode

    def set_total_percent_profit(self, tpprofit):
        self._tpprofit = tpprofit

    def get_total_percent_profit(self):
        return self._tpprofit

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

    def get_account_status(self):
        return self.client.get_account_status()

    # get USDT value of base by calculating (base_currency) * (currency_usdt)
    def get_usdt_value_symbol(self, symbol, price=0):
        currency = self.split_ticker_id(symbol)[1]
        if currency == 'USDT':
            currency_price = 1.0
        else:
            usdt_symbol = self.make_ticker_id(currency, 'USDT')
            currency_price = float(self.get_ticker(usdt_symbol))

        if not currency_price:
            return 0

        if not price:
            price = float(self.get_ticker(symbol))

        if not price:
            return 0

        return currency_price * price

    def get_deposit_history(self, asset=None):
        return self.client.get_deposit_history(asset=asset)
