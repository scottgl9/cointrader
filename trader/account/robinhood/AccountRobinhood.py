from trader.account.AccountBase import AccountBase
from trader.lib.struct.Order import Order
from trader.lib.struct.AssetInfo import AssetInfo
import trader.account.robinhood.robin_stocks as r
from .AccountRobinhoodInfo import AccountRobinhoodInfo
from .AccountRobinhoodBalance import AccountRobinhoodBalance
from .AccountRobinhoodTrade import AccountRobinhoodTrade
from trader.config import *
import json
import os
import time
from datetime import datetime, timedelta
import pyotp
import stix.utils.dates


class AccountRobinhood(AccountBase):
    def __init__(self, client=None, simulation=False, logger=None, simulate_db_filename=None):
        super(AccountRobinhood, self).__init__(client, simulation, logger, simulate_db_filename)
        self.exchange_type = AccountBase.EXCHANGE_ROBINHOOD
        self.exchange_name = 'robinhood'
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.logger = logger
        self.simulate = simulation
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

        self.currencies = ['BTC', 'ETH', 'USDC', 'USD']
        self.currency_trade_pairs = ['ETH-BTC', 'BTC-USDC', 'ETH-USDC', 'BTC-USD', 'ETH-USD']

        self.info = AccountRobinhoodInfo(client, simulation, logger, self.exchange_info_file)
        self.balance = AccountRobinhoodBalance(client, simulation, logger)
        self.trade = AccountRobinhoodTrade(client, simulation, logger)

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

    def get_ticker(self, symbol=None):
        if not self.simulate:
            if not self.get_info_all_assets():
                self.load_exchange_info()
            sid = self.get_ticker_id(symbol)
            result = self.client.get_crypto_quote_from_id(id=sid)
            if result:
                try:
                    price = float(result['mark_price'])
                except KeyError:
                    price = 0.0
                return price
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

    def is_currency(self, name):
        if name in self.currencies:
            return True
        return False

    def is_currency_pair(self, symbol=None, base=None, currency=None):
        if not base or not currency:
            base, currency = self.split_ticker_id(symbol)
        if not base or not currency:
            return False
        if base not in self.currencies:
            return False
        if currency not in self.currencies:
            return False
        return True

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

    def split_symbol(self, symbol):
        return self.split_ticker_id(symbol)

    def get_symbol_base(self, symbol):
        result = self.split_ticker_id(symbol)
        if result:
            return result[0]
        return None

    def get_symbol_currency(self, symbol):
        result = self.split_ticker_id(symbol)
        if result:
            return result[1]
        return None

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

    # return asset info in AssetInfo class object
    def get_asset_info(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return None

        min_qty=info['min_qty']

        try:
            min_notional=info['minNotional']
        except KeyError:
            min_notional = min_qty

        if float(min_qty) < float(min_notional):
            min_qty = min_notional
        min_price=info['min_price']
        base_step_size=info['base_step_size']
        currency_step_size=info['currency_step_size']
        is_currency_pair = self.is_currency_pair(symbol=symbol, base=base, currency=currency)

        try:
            baseAssetPrecision = info['baseAssetPrecision']
            quotePrecision = info['quotePrecision']
        except KeyError:
            baseAssetPrecision = 8
            quotePrecision = 8

        orderTypes = []

        try:
            for order_type in info['orderTypes']:
                orderTypes.append(Order.get_order_msg_type(order_type))
        except KeyError:
            pass

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


    # determine if asset is available (not disabled or delisted)
    # if not, don't trade
    def is_asset_available(self, name):
        status = self.get_asset_status(name)
        try:
            if status['disabled']:
                return False
            if status['delisted']:
                return False
        except KeyError:
            return False
        return True

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

    def get_all_ticker_symbols(self, currency=None):
        if not self._exchange_pairs:
            self.load_exchange_info()
        return self._exchange_pairs

    def get_all_tickers(self):
        pass
    #    result = {}
    #    if not self.simulate:
    #        for ticker in self.client.get_product_ticker()
    #            result[ticker['symbol']] = ticker['price']
    #    else:
    #        result = self._tickers
    #    return result

    def get_order(self, order_id, ticker_id):
        return self.client.get_order(order_id=order_id)

    def buy_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            return self.buy_market_simulate(size, price, ticker_id)
        else:
            self.logger.info("buy_market({}, {}, {})".format(size, price, ticker_id))
            result = self.client.place_market_order(product_id=ticker_id, side='buy', size=size)
            return result

    def sell_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            return self.sell_market_simulate(size, price, ticker_id)
        else:
            self.logger.info("sell_market({}, {}, {})".format(size, price, ticker_id))
            result = self.client.place_market_order(product_id=ticker_id, side='sell', size=size)
            return result

    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            return self.buy_limit_stop_simulate(price, size, stop_price, ticker_id)
        else:
            self.logger.info("buy_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.place_stop_order(product_id=ticker_id, side='buy', price=price, size=size)

    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):

        if self.simulate:
            return self.sell_limit_stop_simulate(price, size, stop_price, ticker_id)
        else:
            self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.place_stop_order(product_id=ticker_id, side='sell', price=price, size=size)

    def buy_limit(self, price, size, ticker_id=None):
        if self.simulate:
            return self.buy_limit_simulate(price, size, ticker_id)
        else:
            return self.client.place_limit_order(product_id=ticker_id, side='buy', price=price, size=size)

    def sell_limit(self, price, size, ticker_id=None):
        if self.simulate:
            return self.sell_limit_simulate(price, size, ticker_id)
        else:
            return self.client.place_limit_order(product_id=ticker_id, side='sell', price=price, size=size)

    def cancel_order(self, orderid, ticker_id=None):
        return self.client.cancel_order(order_id=orderid)

    def cancel_all(self, ticker_id=None):
        pass

    # The granularity field must be one of the following values: {60, 300, 900, 3600, 21600, 86400}
    # The maximum amount of data returned is 300 candles
    # kline format: [ timestamp, low, high, open, close, volume ]
    def get_klines(self, days=0, hours=1, ticker_id=None):
        end = datetime.utcnow()
        start = (end - timedelta(days=days, hours=hours))
        granularity = 900
        if days == 0 and hours < 6:
            granularity = 60
        elif (days== 0 and hours <= 24) or (days == 1 and hours == 0):
            granularity = 300

        rates = self.pc.get_product_historic_rates(ticker_id,
                                                   start.isoformat(),
                                                   end.isoformat(),
                                                   granularity=granularity)
        return rates[::-1]


    def get_hourly_klines(self, symbol, start_ts, end_ts, reverse=False):
        result = []
        if not reverse:
            ts1 = start_ts
            ts2 = end_ts
            while ts1 <= end_ts:
                ts2 = end_ts
                if (ts2 - ts1) > 3600 * 250:
                    ts2 = ts1 + 3600 * 250
                start = self.ts_to_iso8601(ts1)
                end = self.ts_to_iso8601(ts2)

                klines = self.pc.get_product_historic_rates(product_id=symbol,
                                                            start=start,
                                                            end=end,
                                                            granularity=3600)
                ts1 = ts2 + 3600
                if isinstance(klines, list):
                    try:
                        if len(klines):
                            result += reversed(klines)
                    except TypeError:
                        print(klines, type(klines))
                        pass
                    time.sleep(1)
                else:
                    if klines['message'] == 'NotFound':
                        time.sleep(1)
                        continue
                    print("ERROR get_hourly_klines(): {}".format(klines['message']))
                    return result
        # else:
        #     ts1 = start_ts
        #     ts2 = end_ts
        #     while ts1 >= start_ts:
        #         ts1 = start_ts
        #         if (ts2 - ts1) > 3600 * 250:
        #             ts1 = ts2 - 3600 * 250
        #         start = self.ts_to_iso8601(ts1)
        #         end = self.ts_to_iso8601(ts2)
        #         klines = self.pc.get_product_historic_rates(product_id=symbol,
        #                                                     start=start,
        #                                                     end=end,
        #                                                     granularity=3600)
        #         ts1 = ts2 - 3600
        #         if isinstance(klines, list):
        #             try:
        #                 result = reversed(klines) + result
        #             except TypeError:
        #                 pass
        #             time.sleep(1)
        #         else:
        #             if klines['message'] == 'NotFound':
        #                 break
        #             print("ERROR get_hourly_klines(): {}".format(klines['message']))
        #             return result

        return result
