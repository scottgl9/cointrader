# handle multiple TraiePairs, one for each base / currency we want to trade
from trader.account.AccountBinance import AccountBinance
from trader.OrderHandler import OrderHandler

from trader.TradePair import TradePair
from trader.MarketManager import MarketManager
from trader.lib.Kline import Kline
from trader.lib.MessageHandler import Message, MessageHandler
from trader.strategy.global_strategy.global_obv_strategy import global_obv_strategy
from datetime import datetime




# handle incoming websocket messages for all symbols, and create new tradepairs
# for those that do not yet exist
class MultiTrader(object):
    def __init__(self, client, strategy_name='', signal_names=None, assets_info=None,
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
        tick_size = 0.0
        min_notional = 0.0

        base_name, currency_name = self.accnt.split_symbol(symbol)

        if not base_name or not currency_name: return None

        # if an asset has deposit disabled, means its probably suspended
        # or de-listed so DO NOT trade this coin
        if self.accnt.deposit_asset_disabled(base_name):
            return None

        asset_info = self.accnt.get_asset_info_dict(symbol)
        if not asset_info:
            return None

        # *FIXME* use AssetInfo class instead
        base_min_size = float(asset_info['stepSize'])
        tick_size = float(asset_info['tickSize'])
        min_notional = float(asset_info['minNotional'])

        if min_notional > base_min_size:
            base_min_size = min_notional

        # optimization: if balance of ETH or BNB is less than
        # minimum trade amount, do not process trade pairs with currency
        # ETH or BNB respectively
        #if self.simulate and currency_name == "ETH" and "ETHBTC" in self.assets_info:
        #    minqty = float(self.assets_info["ETHBTC"]['minQty'])
        #    balance = self.accnt.get_asset_balance("ETH")["balance"]
        #    if balance < minqty:
        #        return
        #if self.simulate and currency_name == "BNB" and "BNBBTC" in self.assets_info:
        #    minqty = float(self.assets_info["BNBBTC"]['minQty'])
        #    balance = self.accnt.get_asset_balance("BNB")["balance"]
        #    if balance < minqty:
        #        return

        trade_pair = TradePair(self.client,
                               self.accnt,
                               strategy_name=self.strategy_name,
                               signal_names=self.signal_names,
                               base=base_name,
                               currency=currency_name,
                               asset_info=self.accnt.get_asset_info(base=base_name, currency=currency_name),
                               base_min_size=base_min_size,
                               tick_size=tick_size,
                               logger=self.logger)

        self.trade_pairs[symbol] = trade_pair

        if not self.simulate and self.order_handler.trader_db:
            # if balance of coin is less than base_min_size, remove from trade db
            balance = self.accnt.round_base(float(self.accnt.get_asset_balance(base_name)['balance']))
            if balance >= base_min_size:
                self.order_handler.trade_db_load_symbol(symbol, trade_pair)
                #self.order_handler.trader_db.remove_trade(symbol)
                #self.logger.info("ALREADY_SOLD for {}, removed from trade db".format(symbol))
            #else:
            #    self.order_handler.trade_db_load_symbol(symbol, trade_pair)
        return trade_pair

    def update_initial_btc(self):
        self.order_handler.update_initial_btc()

    def get_stored_trades(self):
        return self.order_handler.get_stored_trades()

    def get_trader(self, symbol):
        #if symbol not in self.trade_pairs.keys():
        #    self.add_trade_pair(symbol)
        try:
            result = self.trade_pairs[symbol]
        except KeyError:
            result = self.add_trade_pair(symbol)
            #result = self.trade_pairs[symbol]
        return result

    def process_message(self, kline, cache_db=None):
        self.current_ts = kline.ts

        symbol_trader = self.get_trader(kline.symbol)
        if not symbol_trader:
            return None

        # keep track of all current price values for all symbols being processed
        self.accnt.update_ticker(kline.symbol, kline.close)

        # compute current total percent profit, and update info in strategy
        tpprofit = self.order_handler.get_total_percent_profit()
        if tpprofit != 0:
            symbol_trader.update_total_percent_profit(tpprofit)

        # use market manager
        if symbol_trader.mm_enabled():
            self.market_manager.update(kline.symbol, kline)
            if self.market_manager.ready():
                for k in self.market_manager.get_klines():
                    self.trade_pairs[k.symbol].run_update(kline, mmkline=k)
                self.market_manager.reset()
        else:
            symbol_trader.run_update(kline, cache_db=cache_db)

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

                    # keep asset details up to date
                    self.accnt.load_detail_all_assets()

                    self.last_ts = self.current_ts
                    timestr = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    self.logger.info("MultiTrader running {}".format(timestr))

        # handle incoming messages
        self.order_handler.process_order_messages()

        if self.accnt.simulate:
            return symbol_trader
        return None

    # process message from user event socket
    # cmd: NEW, PARTIALLY_FILLED, FILLED, CANCELED
    # types: MARKET, LIMIT
    # side: BUY, SELL
    # other fields: price, size
    def process_user_message(self, msg):
        if self.last_ts == 0 or self.current_ts == 0:
            return


        # *TODO* handle external completed sells
        #if msg['X'] == 'FILLED' and msg['S'] == 'SELL':
        #    symbol = msg['s']
        #    price = float(msg['p'])
        #    size = float(msg['q'])
        #    self.msg_handler.sell_complete(symbol, price, size, buy_price=0, sig_id=0)

        if (self.current_ts - self.last_ts) > self.check_ts_min:
            self.accnt.get_account_balances()
            self.last_ts = self.current_ts
            timestr = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            self.logger.info("MultiTrader running {}".format(timestr))

    def update_tickers(self, tickers):
        self.tickers = tickers
        if self.order_handler:
            self.order_handler.update_tickers(self.tickers)
