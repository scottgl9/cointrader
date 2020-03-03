from trader.account.bittrex.bittrex import Bittrex, API_V2_0
from trader.account.AccountBase import AccountBase
from .AccountBittrexInfo import AccountBittrexInfo
from .AccountBittrexBalance import AccountBittrexBalance
from .AccountBittrexTrade import AccountBittrexTrade
from trader.lib.struct.TraderMessage import TraderMessage
from trader.lib.struct.Order import Order
from trader.lib.struct.OrderUpdate import OrderUpdate
from trader.lib.struct.AssetInfo import AssetInfo
from trader.config import *

import json
import os


#logger = logging.getLogger(__name__)

class AccountBittrex(AccountBase):
    def __init__(self, client=None, simulation=False, logger=None, simulate_db_filename=None):
        super(AccountBittrex, self).__init__(client, simulation, logger, simulate_db_filename)
        self.exchange_type = AccountBase.EXCHANGE_BITTREX
        self.exchange_name = 'bittrex'
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.logger = logger
        self.simulate_db_filename = simulate_db_filename
        if client:
            self.client = client
        else:
            self.client = Bittrex(api_key=BITTREX_API_KEY, api_secret=BITTREX_API_SECRET, api_version=API_V2_0)
        self.simulate = simulation
        self.info_all_assets = {}
        self.details_all_assets = {}
        self.balances = {}
        self._trader_mode = AccountBase.TRADER_MODE_NONE

        # sub module implementations
        self.info = AccountBittrexInfo(client, simulation, logger, self.exchange_info_file)
        self.balance = AccountBittrexBalance(client, simulation, logger)
        self.trade = AccountBittrexTrade(client, simulation, logger)

        # keep track of initial currency buy size, and subsequent trades against currency
        self._currency_buy_size = {}
        for currency in self.info.get_currencies():
            self._currency_buy_size[currency] = 0

        self.client = client

        self._tickers = {}
        self._min_tickers = {}
        self._max_tickers = {}
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

    def get_trader_mode(self):
        return self._trader_mode

    def set_trader_mode(self, trader_mode):
        self._trader_mode = trader_mode

    def trade_mode_hourly(self):
        return self._trader_mode == AccountBase.TRADER_MODE_HOURLY

    def trade_mode_realtime(self):
        return self._trader_mode == AccountBase.TRADER_MODE_REALTIME

    def format_ts(self, ts):
        return int(ts)

    def ts_to_seconds(self, ts):
        return float(ts / 1000.0)

    # returns true if this ts is an hourly ts
    def is_hourly_ts(self, ts):
        hourly_ts = self.get_hourly_ts(ts)
        return int(ts) == hourly_ts

    # set minutes and seconds components of timestamp to zero
    def get_hourly_ts(self, ts):
        #dt = datetime.utcfromtimestamp(self.ts_to_seconds(ts)).replace(minute=0, second=0)
        #return int(self.seconds_to_ts(time.mktime(dt.timetuple())))
        return int(self.ts_to_seconds(ts) / 3600.0) * 3600 * 1000

    def seconds_to_ts(self, seconds):
        return float(seconds * 1000)

    def hours_to_ts(self, hours):
        return float(hours * 3600 * 1000)

    # if hourly table name doesn't match symbol name
    # ex. symbol 'BTC-USD', table name 'BTC_USD'
    def get_hourly_table_name(self, symbol):
        return symbol

    # get symbol name from hourly table name
    # ex. table name 'BTC_USD', return symbol 'BTC-USD'
    def get_symbol_hourly_table(self, table_name):
        return table_name

    def get_ticker(self, symbol):
        if not self.simulate and len(self._tickers) == 0:
            self._tickers = self.get_all_tickers()
        try:
            price = self._tickers[symbol]
        except KeyError:
            price = 0.0
        return price

    def update_ticker(self, symbol, price, ts):
        if self.simulate:
            last_price = 0
            try:
                last_price = self._tickers[symbol]
            except KeyError:
                pass

            if not last_price:
                self._min_tickers[symbol] = [price, ts]
                self._max_tickers[symbol] = [price, ts]
            else:
                if price < self._min_tickers[symbol][0]:
                    self._min_tickers[symbol] = [price, ts]
                elif price > self._max_tickers[symbol][0]:
                    self._max_tickers[symbol] = [price, ts]

        self._tickers[symbol] = price

    def update_tickers(self, tickers):
        for symbol, price in tickers.items():
            self._tickers[symbol] = float(price)

    def get_tickers(self):
        return self._tickers

    def get_min_tickers(self):
        return self._min_tickers

    def get_max_tickers(self):
        return self._max_tickers

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
        base_increment = self.get_asset_info_dict(symbol=symbol, field='stepSize')
        return self.round_base(price, base_increment)

    def round_quantity_symbol(self, symbol, size):
        min_qty = self.get_asset_info_dict(symbol=symbol, field='minQty')
        return self.round_quantity(size, min_qty)

    def round_quote_symbol(self, symbol, price):
        quote_increment = self.get_asset_info_dict(symbol=symbol, field='tickSize')
        return self.round_quote(price, quote_increment)

    def round_quote_pair(self, base, currency, price):
        quote_increment = self.get_asset_info_dict(base=base, currency=currency, field='tickSize')
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
        return info['stepSize']

    def get_currency_step_size(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return 0
        return info['tickSize']

    # return asset info in AssetInfo class object
    def get_asset_info(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return None

        min_qty=info['minQty']
        min_notional=info['minNotional']
        if float(min_qty) < float(min_notional):
            min_qty = min_notional
        min_price=info['minPrice']
        base_step_size=info['stepSize']
        currency_step_size=info['tickSize']
        is_currency_pair = self.is_currency_pair(symbol=symbol, base=base, currency=currency)
        baseAssetPrecision = info['baseAssetPrecision']
        quotePrecision = info['quotePrecision']
        orderTypes = []
        for order_type in info['orderTypes']:
            orderTypes.append(Order.get_order_msg_type(order_type))

        result = AssetInfo(base=base,
                           currency=currency,
                           min_qty=min_qty,
                           min_price=min_price,
                           base_step_size=base_step_size,
                           currency_step_size=currency_step_size,
                           is_currency_pair=is_currency_pair,
                           baseAssetPrecision=baseAssetPrecision,
                           quotePrecision=quotePrecision,
                           orderTypes=orderTypes
                           )
        return result

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

    def get_all_ticker_symbols(self, currency=None):
        result = []
        if not self.simulate:
            for ticker in self.client.get_all_tickers():
                if currency and ticker['symbol'].endswith(currency):
                    result.append(ticker['symbol'])
                elif not currency:
                    result.append(ticker['symbol'])
        else:
            result = self.info_all_assets.keys()
        return result

    def get_all_tickers(self):
        result = {}
        if not self.simulate:
            info_tickers = self.client.get_market_summaries()
            if not info_tickers['success']:
                return result
            for info in info_tickers['result']:
                #market_info = info['Market']
                market_summary = info['Summary']
                ticker_id = market_summary['MarketName']
                price = market_summary['Last']
                result[ticker_id] = price
        else:
            result = self._tickers
        return result

    def get_klines(self, days=0, hours=1, ticker_id=None):
        timestr = ''
        if days == 1:
            timestr = "1 day ago"
        elif days > 1:
            timestr = "{} days ago".format(days)
        if days == 0:
            if hours == 1:
                timestr = "1 hour ago"
            elif hours > 1:
                timestr = "{} hours ago".format(hours)
        else:
            if hours == 1:
                timestr = "and 1 hour ago"
            elif hours > 1:
                timestr = "and {} hours ago".format(hours)
        timestr += " UTC"

        klines_data = self.client.get_historical_klines(ticker_id, Client.KLINE_INTERVAL_1MINUTE, timestr)

        # reorganize kline format to same as GDAX for consistency:
        # GDAX kline format: [ timestamp, low, high, open, close, volume ]
        # binance format: [opentime, open, high, low, close, volume, closetime quotevolume, tradecount,
        # taker_buy_base_volume, taker_buy_currency_volume, ignore]
        klines = []
        for k in klines_data:
            ts = k[0] / 1000
            klines.append([ts, k[3], k[2], k[1], k[4], k[5]])

        return klines

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        klines = self.client.get_historical_klines_generator(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            start_str=start_ts,
            end_str=end_ts,
        )

        return klines
