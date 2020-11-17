from trader.account.binance.binance.client import Client, BinanceAPIException
from trader.account.AccountBase import AccountBase
from .AccountBinanceInfo import AccountBinanceInfo
from .AccountBinanceBalance import AccountBinanceBalance
from .AccountBinanceTrade import AccountBinanceTrade
from .AccountBinanceMarket import AccountBinanceMarket
from trader.lib.struct.TraderMessage import TraderMessage
from trader.lib.struct.Order import Order
from trader.lib.struct.OrderUpdate import OrderUpdate
from trader.lib.struct.AssetInfo import AssetInfo
from trader.lib.struct.Exchange import Exchange
import json
import os


class AccountBinance(AccountBase):
    def __init__(self, client, simulate=False, live=False, logger=None, simulate_db_filename=None):
        super(AccountBinance, self).__init__(client, simulate, live, logger, simulate_db_filename)
        self.exchange_type = Exchange.EXCHANGE_BINANCE
        self.exchange_name = Exchange.name(self.exchange_type)
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.logger = logger
        self.simulate_db_filename = simulate_db_filename
        self.client = client
        self.simulate = simulate
        self.live = live
        #self.balances = {}

        # sub module implementations
        self.info = AccountBinanceInfo(client, simulate, logger)
        self.trade = AccountBinanceTrade(client, self.info, simulate, logger)
        self.market = AccountBinanceMarket(client, self.info, simulate, logger)
        self.balance = AccountBinanceBalance(client, self.info, self.market, simulate, logger)

        # hourly db column names
        self.hourly_cnames = ['ts', 'open', 'high', 'low', 'close', 'volume']
        #self.hourly_cnames = ['ts', 'open', 'high', 'low', 'close', 'base_volume', 'quote_volume',
        #                      'trade_count', 'taker_buy_base_volume', 'taker_buy_quote_volume']
        # hourly db column names short list
        #self.hourly_scnames = ['ts', 'open', 'high', 'low', 'close', 'base_volume', 'quote_volume']

        # keep track of initial currency buy size, and subsequent trades against currency
        self._currency_buy_size = {}
        for currency in self.info.get_currencies():
            self._currency_buy_size[currency] = 0

        self._trader_profit_mode = 'BTC'
        self._tpprofit = 0
        self.initial_currency = 0
        self._sell_only = False
        self._btc_only = False
        self._eth_only = False
        self._bnb_only = False
        self._hourly_symbols_only = False
        self._trades_disabled = False
        self._test_stop_loss = False
        self._max_market_buy = 0
        self.loaded_model_count = 0

    # get config section name from trader.ini
    def get_config_section_name(self):
        if self.simulate:
            name = "{}.simulate".format(self.exchange_name)
        else:
            name = "{}.live".format(self.exchange_name)
        return name

    def trade_mode_hourly(self):
        return self.info.get_trader_mode() == Exchange.TRADER_MODE_HOURLY

    def trade_mode_realtime(self):
        return self.info.get_trader_mode() == Exchange.TRADER_MODE_REALTIME

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

    # get hourly db column names
    def get_hourly_column_names(self):
        return self.hourly_cnames

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

    def set_sell_only(self, sell_only):
        self.logger.info("set_sell_only({})".format(sell_only))
        self._sell_only = sell_only

    def sell_only(self):
        return self._sell_only

    def set_btc_only(self, btc_only):
        self.logger.info("set_btc_only({})".format(btc_only))
        self._btc_only = btc_only

    def btc_only(self):
        return self._btc_only

    def set_eth_only(self, eth_only):
        self.logger.info("set_eth_only({})".format(eth_only))
        self._eth_only = eth_only

    def eth_only(self):
        return self._eth_only

    def set_bnb_only(self, bnb_only):
        self.logger.info("set_bnb_only({})".format(bnb_only))
        self._bnb_only = bnb_only

    def bnb_only(self):
        return self._bnb_only

    def set_hourly_symbols_only(self, hourly_symbols_only):
        self.logger.info("set_hourly_symbols_only({})".format(hourly_symbols_only))
        self._hourly_symbols_only = hourly_symbols_only

    def hourly_symbols_only(self):
        return self._hourly_symbols_only

    def set_trades_disabled(self, trades_disabled):
        self.logger.info("set_trades_disabled({})".format(trades_disabled))
        self._trades_disabled = trades_disabled

    def trades_disabled(self):
        return self._trades_disabled

    def set_max_market_buy(self, max_market_buy):
        self.logger.info("set_max_market_buy({})".format(max_market_buy))
        self._max_market_buy = max_market_buy

    def max_market_buy(self):
        return self._max_market_buy

    def set_test_stop_loss(self, test_stop_loss):
        self.logger.info("set_test_stop_loss({})".format(test_stop_loss))
        self._test_stop_loss = test_stop_loss

    def test_stop_loss(self):
        return self._test_stop_loss

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

    def get_account_history(self):
        pass

    def get_my_trades(self, base, currency, limit=500):
        balances = self.get_account_balances()
        result = []

        symbol = self.make_ticker_id(base, currency)

        amount = 0.0
        if base in balances.keys():
            amount = balances[base]
        actual_fills = {}
        current_amount = 0.0
        orders = self.client.get_my_trades(symbol=symbol, limit=limit)
        for order in orders:
            actual_fills[order['time']] = order

        skip_size = 0.0
        for (k, v) in sorted(actual_fills.items(), reverse=True):
            if v['isBuyer'] == False:
                skip_size += float(v['qty'])
                continue

            if float(v['qty']) <= skip_size:
                skip_size -= float(v['qty'])
                continue

            #if symbol not in result.keys():
            #    result[symbol] = []

            result.append(v)
            current_amount += float(v['qty'])
            if current_amount >= float(amount):
                break
        return result


    # def buy_limit_profit(self, price, size, stop_price, ticker_id=None):
    #     if self.simulate:
    #         base, currency = self.split_ticker_id(ticker_id)
    #         cbalance, cavailable = self.get_asset_balance_tuple(currency)
    #         usd_value = float(price) * float(size)  # self.round_quote(price * size)
    #
    #         if usd_value > cavailable: return False
    #
    #         self.update_asset_balance(currency, cbalance, cavailable - usd_value)
    #         return True
    #     else:
    #         self.logger.info("buy_limit_profit({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
    #         return self.client.create_order(symbol=ticker_id,
    #                                  timeInForce=Client.TIME_IN_FORCE_GTC,
    #                                  side=Client.SIDE_BUY,
    #                                  type=Client.ORDER_TYPE_TAKE_PROFIT_LIMIT,
    #                                  quantity=size,
    #                                  price=price,
    #                                  stopPrice=stop_price)
    #
    #
    # def sell_limit_profit(self, price, size, stop_price, ticker_id=None):
    #
    #     if self.simulate:
    #         #self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
    #         base, currency = self.split_ticker_id(ticker_id)
    #         bbalance, bavailable = self.get_asset_balance_tuple(base)
    #
    #         if float(size) > bavailable: return False
    #
    #         self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
    #         return True
    #     else:
    #         self.logger.info("sell_limit_profit({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
    #         return self.client.create_order(symbol=ticker_id,
    #                                  timeInForce=Client.TIME_IN_FORCE_GTC,
    #                                  side=Client.SIDE_SELL,
    #                                  type=Client.ORDER_TYPE_TAKE_PROFIT_LIMIT,
    #                                  quantity=size,
    #                                  price=price,
    #                                  stopPrice=stop_price)
    #
    #
    # def buy_market_profit(self, price, size, stop_price, ticker_id=None):
    #     if self.simulate:
    #         base, currency = self.split_ticker_id(ticker_id)
    #         cbalance, cavailable = self.get_asset_balance_tuple(currency)
    #         usd_value = float(price) * float(size)  # self.round_quote(price * size)
    #
    #         if usd_value > cavailable: return False
    #
    #         self.update_asset_balance(currency, cbalance, cavailable - usd_value)
    #         return True
    #     else:
    #         self.logger.info("buy_market_profit({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
    #         return self.client.create_order(symbol=ticker_id,
    #                                  side=Client.SIDE_BUY,
    #                                  type=Client.ORDER_TYPE_TAKE_PROFIT,
    #                                  quantity=size,
    #                                  stopPrice=stop_price)
    #
    #
    # def sell_market_profit(self, price, size, stop_price, ticker_id=None):
    #     if self.simulate:
    #         #self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
    #         base, currency = self.split_ticker_id(ticker_id)
    #         bbalance, bavailable = self.get_asset_balance_tuple(base)
    #
    #         if float(size) > bavailable: return False
    #
    #         self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
    #         return True
    #     else:
    #         self.logger.info("sell_market_profit({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
    #         return self.client.create_order(symbol=ticker_id,
    #                                  side=Client.SIDE_SELL,
    #                                  type=Client.ORDER_TYPE_TAKE_PROFIT,
    #                                  quantity=size,
    #                                  stopPrice=stop_price)
    #
    #
    # def buy_market_stop(self, price, size, stop_price, ticker_id=None):
    #     if self.simulate:
    #         base, currency = self.split_ticker_id(ticker_id)
    #         cbalance, cavailable = self.get_asset_balance_tuple(currency)
    #         usd_value = float(price) * float(size)  # self.round_quote(price * size)
    #
    #         if usd_value > cavailable: return False
    #
    #         self.update_asset_balance(currency, cbalance, cavailable - usd_value)
    #         return True
    #     else:
    #         self.logger.info("buy_market_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
    #         return self.client.create_order(symbol=ticker_id,
    #                                  side=Client.SIDE_BUY,
    #                                  type=Client.ORDER_TYPE_STOP_LOSS,
    #                                  quantity=size,
    #                                  stopPrice=stop_price)
    #
    #
    # def sell_market_stop(self, price, size, stop_price, ticker_id=None):
    #
    #     if self.simulate:
    #         #self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
    #         base, currency = self.split_ticker_id(ticker_id)
    #         bbalance, bavailable = self.get_asset_balance_tuple(base)
    #
    #         if float(size) > bavailable: return False
    #
    #         self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
    #         return True
    #     else:
    #         self.logger.info("sell_market_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
    #         return self.client.create_order(symbol=ticker_id,
    #                                  side=Client.SIDE_SELL,
    #                                  type=Client.ORDER_TYPE_STOP_LOSS,
    #                                  quantity=size,
    #                                  stopPrice=stop_price)
