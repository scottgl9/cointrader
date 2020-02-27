#from abc import ABCMeta, abstractmethod
from trader.lib.struct.Order import Order


class AccountBase(object):
    EXCHANGE_UNKNOWN = 0
    EXCHANGE_BINANCE = 1
    EXCHANGE_CBPRO = 2
    EXCHANGE_BITTREX = 3
    EXCHANGE_KRAKEN = 4
    EXCHANGE_POLONIEX = 5
    EXCHANGE_ROBINHOOD = 6
    # trader modes
    TRADER_MODE_NONE = 0
    TRADER_MODE_REALTIME = 1
    TRADER_MODE_HOURLY = 2

    def __init__(self, client, simulation=False, logger=None, simulate_db_filename=None):
        self.logger = logger
        self.simulate_db_filename = simulate_db_filename
        self.client = client
        self.simulate = simulation

        # account specific components
        self.info = None
        self.balance = None
        self.trade = None

    def get_config_section_name(self):
        pass

    def get_trader_mode(self):
        pass

    def set_trader_mode(self, trader_mode):
        pass

    def trade_mode_hourly(self):
        pass

    def trade_mode_realtime(self):
        pass

    def ts_to_seconds(self, ts):
        pass

    def is_hourly_ts(self, ts):
        pass

    def get_hourly_ts(self, ts):
        pass

    def seconds_to_ts(self, seconds):
        pass

    def hours_to_ts(self, hours):
        pass

    def get_hourly_table_name(self, symbol):
        pass

    def get_symbol_hourly_table(self, table_name):
        pass

    def get_hourly_column_names(self):
        pass

    def round_base_symbol(self, symbol, price):
        return 0

    def round_quote_symbol(self, symbol, price):
        return 0

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

    # 'info' component functions
    def make_ticker_id(self, base, currency):
        return self.info.make_ticker_id(base, currency)

    def split_ticker_id(self, symbol):
        return self.info.split_ticker_id(symbol)

    def get_currencies(self):
        return self.info.get_currencies()

    def get_info_all_assets(self):
        return self.info.get_info_all_assets()

    def get_details_all_assets(self):
        return self.info.get_info_all_assets()

    def load_exchange_info(self):
        return self.info.load_exchange_info()

    def get_exchange_info(self):
        return self.info.get_exchange_info()

    def parse_exchange_info(self, pair_info, asset_info):
        return self.info.parse_exchange_info(pair_info, asset_info)

    def get_exchange_pairs(self):
        return self.info.get_exchange_pairs()

    def is_exchange_pair(self, symbol):
        return self.info.is_exchange_pair(symbol)

    def get_asset_status(self, name=None):
        return self.info.get_asset_status(name)

    def get_asset_info_dict(self, symbol=None, base=None, currency=None, field=None):
        return self.info.get_asset_info_dict(symbol, base, currency, field)

    def is_asset_available(self, name):
        return self.info.is_asset_available(name)

    # 'balance' component functions
    def get_account_total_value(self, currency, detailed=False):
        return self.balance.get_account_total_value(currency, detailed)

    def get_account_balances(self, detailed=False):
        return self.balance.get_account_balances(detailed)

    def get_balances(self):
        return self.balance.get_balances()

    def get_asset_balance(self, asset):
        return self.balance.get_asset_balance(asset)

    def get_asset_balance_tuple(self, asset):
        return self.balance.get_asset_balance_tuple(asset)

    def update_asset_balance(self, name, balance, available):
        return self.balance.update_asset_balance(name, balance, available)

    # 'trade' component functions
    def buy_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            return self.buy_market_simulate(size, price, ticker_id)
        else:
            return self.trade.buy_market(size, price, ticker_id)

    def sell_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            return self.sell_market_simulate(size, price, ticker_id)
        else:
            return self.trade.sell_market(size, price, ticker_id)

    def buy_limit(self, price, size, ticker_id=None):
        if self.simulate:
            return self.buy_limit_simulate(price, size, ticker_id)
        else:
            return self.trade.buy_limit(size, price, ticker_id)

    def sell_limit(self, price, size, ticker_id=None):
        if self.simulate:
            return self.sell_limit_simulate(size, price, ticker_id)
        else:
            return self.trade.sell_limit(size, price, ticker_id)

    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            return self.buy_limit_stop_simulate(price, size, stop_price, ticker_id)
        else:
            return self.trade.buy_limit_stop(price, size, stop_price, ticker_id)

    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            return self.sell_limit_stop_simulate(price, size, stop_price, ticker_id)
        else:
            return self.trade.sell_limit_stop(price, size, stop_price, ticker_id)

    # simulate buy market order
    def buy_market_simulate(self, size, price=0.0, ticker_id=None):
        size = self.round_base_symbol(ticker_id, size)
        base, currency = self.split_ticker_id(ticker_id)
        bbalance, bavailable = self.get_asset_balance_tuple(base)
        cbalance, cavailable = self.get_asset_balance_tuple(currency)
        amount = self.round_quote_symbol(ticker_id, float(price) * float(size))
        if amount > cavailable:
            return False

        self.update_asset_balance(base, bbalance + float(size), bavailable + float(size))
        self.update_asset_balance(currency, cbalance - amount, cavailable - amount)
        return True

    # simulate sell market order
    def sell_market_simulate(self, size, price=0.0, ticker_id=None):
        base, currency = self.split_ticker_id(ticker_id)
        bbalance, bavailable = self.get_asset_balance_tuple(base)
        cbalance, cavailable = self.get_asset_balance_tuple(currency)

        if float(size) > bavailable:
            #if self.logger:
            #    self.logger.warning("{}: {} > {}".format(ticker_id, float(size), bavailable))
            return False

        amount = self.round_quote_symbol(ticker_id, float(price) * float(size))
        self.update_asset_balance(base, float(bbalance) - float(size), float(bavailable) - float(size))
        self.update_asset_balance(currency, cbalance + amount, cavailable + amount)
        return True

    # simulate buy limit order
    def buy_limit_simulate(self, price, size, ticker_id=None):
        base, currency = self.split_ticker_id(ticker_id)
        cbalance, cavailable = self.get_asset_balance_tuple(currency)
        usd_value = float(price) * float(size)  # self.round_quote(price * size)

        if usd_value > cavailable: return

        self.update_asset_balance(currency, cbalance, cavailable - usd_value)

    # simulate sell limit order
    def sell_limit_simulate(self, price, size, ticker_id=None):
        base, currency = self.split_ticker_id(ticker_id)
        bbalance, bavailable = self.get_asset_balance_tuple(base)

        if float(size) > bavailable: return

        self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))

    # simulate buy limit stop order
    def buy_limit_stop_simulate(self, price, size, stop_price, ticker_id=None):
        base, currency = self.split_ticker_id(ticker_id)
        cbalance, cavailable = self.get_asset_balance_tuple(currency)
        usd_value = float(price) * float(size)  # self.round_quote(price * size)

        if usd_value > cavailable: return False

        self.update_asset_balance(currency, cbalance, cavailable - usd_value)
        return True

    # simulate sell limit stop order
    def sell_limit_stop_simulate(self, price, size, stop_price, ticker_id=None):
        # self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
        base, currency = self.split_ticker_id(ticker_id)
        bbalance, bavailable = self.get_asset_balance_tuple(base)

        if float(size) > bavailable: return False

        self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
        return True

    # use for both limit orders and stop loss orders
    def buy_limit_complete(self, price, size, ticker_id, simulate):
        if simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = float(price) * float(size) #self.round_quote(price * size)
            if usd_value > cbalance: return False
            #print("buy_market({}, {}, {}".format(size, price, ticker_id))
            self.update_asset_balance(base, bbalance + float(size), bavailable + float(size))
            self.update_asset_balance(currency, cbalance - usd_value, cavailable)
            return True
        else:
            self.get_account_balances()

    # use for both limit orders and stop loss orders
    def sell_limit_complete(self, price, size, ticker_id, simulate):
        if simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)

            if float(size) > bbalance: return False

            usd_value = float(price) * float(size)
            self.update_asset_balance(base, float(bbalance) - float(size), float(bavailable))
            self.update_asset_balance(currency, cbalance + usd_value, cavailable + usd_value)
            return True
        else:
            self.get_account_balances()

    # for handling a canceled sell order during simulation
    def cancel_sell_limit_complete(self, size, ticker_id):
        #if not self.simulate:
        #    return
        base, currency = self.split_ticker_id(ticker_id)
        bbalance, bavailable = self.get_asset_balance_tuple(base)
        self.update_asset_balance(base, float(bbalance), float(bavailable) + float(size))

    def get_order(self, order_id, ticker_id):
        if not self.simulate:
            return self.trade.get_order(order_id, ticker_id)

    def get_orders(self, ticker_id=None):
        if not self.simulate:
            return self.trade.get_orders(ticker_id)

    def cancel_order(self, orderid, ticker_id=None):
        if not self.simulate:
            return self.trade.cancel_order(orderid, ticker_id)

    def parse_order_update(self, result):
        return self.trade.parse_order_update(result)

    # parse json response to order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        return self.trade.parse_order_result(result, symbol, sigid)

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        pass
