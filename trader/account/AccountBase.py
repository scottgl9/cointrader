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

    def make_ticker_id(self, base, currency):
        pass

    def split_ticker_id(self, symbol):
        return None, None

    def split_symbol(self, symbol):
        return None, None

    def get_symbol_base(self, symbol):
        pass

    def get_symbol_currency(self, symbol):
        pass

    # 'info' component functions
    def load_exchange_info(self):
        pass

    def get_exchange_info(self):
        pass

    def parse_exchange_info(self, pair_info, asset_info):
        pass

    def get_exchange_pairs(self):
        pass

    def is_exchange_pair(self, symbol):
        pass

    def is_asset_available(self, name):
        pass

    # 'balance' component functions
    def get_account_total_value(self, currency, detailed=False):
        pass

    def get_account_balances(self, detailed=False):
        pass

    def get_asset_balance_tuple(self, asset):
        return 0, 0

    def update_asset_balance(self, name, balance, available):
        pass

    # 'trade' component functions
    def buy_market(self, size, price=0.0, ticker_id=None):
        pass

    def sell_market(self, size, price=0.0, ticker_id=None):
        pass

    def buy_limit(self, price, size, ticker_id=None):
        pass

    def sell_limit(self, price, size, ticker_id=None):
        pass

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

    def cancel_order(self, orderid, ticker_id=None):
        pass

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        pass
