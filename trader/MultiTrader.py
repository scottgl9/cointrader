# handle multiple TraiePairs, one for each base / currency we want to trade
from trader.account.AccountBinance import AccountBinance
from trader.OrderHandler import OrderHandler

from trader.TradePair import TradePair
from trader.MarketManager import MarketManager
from trader.lib.Kline import Kline
from trader.lib.MessageHandler import Message, MessageHandler
from trader.strategy.global_strategy.global_obv_strategy import global_obv_strategy
from datetime import datetime


def split_symbol(symbol):
    base_name = None
    currency_name = None

    #if 'USDT' in symbol: return base_name, currency_name
    currencies = ['BTC', 'ETH', 'BNB', 'USDT']
    for currency in currencies:
        if symbol.endswith(currency):
            currency_name = currency
            base_name = symbol.replace(currency, '')
    return base_name, currency_name


# handle incoming websocket messages for all symbols, and create new tradepairs
# for those that do not yet exist
class MultiTrader(object):
    def __init__(self, client, strategy_name='', signal_names=None, assets_info=None, volumes=None,
                 simulate=False, accnt=None, logger=None, global_en=True, store_trades=False):
        self.trade_pairs = {}
        self.accounts = {}
        self.client = client
        self.simulate = simulate
        self.strategy_name = strategy_name
        self.signal_names = signal_names
        if accnt:
            self.accnt = accnt
        else:
            self.accnt = AccountBinance(self.client, simulation=simulate, logger=logger)
        self.assets_info = assets_info
        self.volumes = volumes
        self.tickers = None
        self.msg_handler = MessageHandler()
        self.market_manager = MarketManager()
        self.logger = logger
        self.notify = None
        self.current_ts = 0
        self.last_ts = 0
        self.check_ts_min = 60 * 1000   # 1 minute
        self.check_ts = 3600 * 1000     # 1 hour
        self.check_count = 0
        self.stopped = False
        self.running = True
        self.store_trades = store_trades
        self.order_handler = OrderHandler(self.accnt, self.msg_handler, self.logger, self.store_trades)
        self.global_strategy = None
        self.global_en = global_en
        if self.global_en:
            self.global_strategy = global_obv_strategy()

        sigstr = None

        if self.signal_names:
            sigstr = ','.join(self.signal_names)

        if self.simulate:
            run_type = "simulation"
        else:
            run_type = "live"

        if sigstr:
            self.logger.info("Running MultiTrade {} strategy {} signal(s) {}".format(run_type, self.strategy_name, sigstr))
        else:
            self.logger.info("Running MultiTrade {} strategy {}".format(run_type, self.strategy_name))


    # create new tradepair handler and select strategy
    def add_trade_pair(self, symbol):
        base_min_size = 0.0
        quote_increment = 0.0
        if symbol in self.assets_info.keys():
            base_min_size = float(self.assets_info[symbol]['minQty'])
            quote_increment = float(self.assets_info[symbol]['tickSize'])

        base_name, currency_name = split_symbol(symbol)
        if not base_name or not currency_name: return

        # if an asset has deposit disabled, means its probably suspended
        # or de-listed so DO NOT trade this coin
        if self.accnt.deposit_asset_disabled(base_name):
            return

        trade_pair = TradePair(self.client, self.accnt, self.strategy_name, self.signal_names, base_name, currency_name)
        self.trade_pairs[symbol] = trade_pair

        if not self.simulate and self.order_handler.trader_db:
            self.order_handler.trade_db_load_symbol(symbol, trade_pair)

    def get_stored_trades(self):
        return self.order_handler.get_stored_trades()

    def get_trader(self, symbol):
        if symbol not in self.trade_pairs.keys():
            self.add_trade_pair(symbol)
        return self.trade_pairs[symbol]

    def process_message(self, kline):
        self.current_ts = kline.ts

        if kline.symbol not in self.trade_pairs.keys():
            self.add_trade_pair(kline.symbol)

        if kline.symbol not in self.trade_pairs.keys():
            return

        symbol_trader = self.trade_pairs[kline.symbol]
        symbol_trader.update_tickers(self.tickers)

        # use market manager
        if symbol_trader.mm_enabled():
            self.market_manager.update(kline.symbol, kline)
            if self.market_manager.ready():
                for k in self.market_manager.get_klines():
                    self.trade_pairs[k.symbol].run_update(kline, mmkline=k)
                self.market_manager.reset()
        else:
            symbol_trader.run_update(kline)

        if self.global_strategy:
            self.global_strategy.run_update(kline)

        self.order_handler.process_limit_order(kline)

        # print alive check message once every 4 hours
        if not self.accnt.simulate:
            if self.last_ts == 0 and self.current_ts != 0:
                self.last_ts = self.current_ts
            elif self.current_ts != 0:
                if (self.current_ts - self.last_ts) > self.check_ts:
                    self.accnt.get_account_balances()
                    self.last_ts = self.current_ts
                    timestr = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    self.logger.info("MultiTrader running {}".format(timestr))

        # handle incoming messages
        self.order_handler.process_order_messages()

    # process message from user event socket
    # cmd: NEW, PARTIALLY_FILLED, FILLED, CANCELED
    # types: MARKET, LIMIT
    # side: BUY, SELL
    # other fields: price, size
    def process_user_message(self, msg):
        if self.last_ts == 0 or self.current_ts == 0:
            return

        if (self.current_ts - self.last_ts) > self.check_ts_min:
            self.accnt.get_account_balances()
            self.last_ts = self.current_ts

    def update_tickers(self, tickers):
        self.tickers = tickers
        if self.order_handler:
            self.order_handler.update_tickers(self.tickers)
