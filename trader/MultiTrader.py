# handle running strategy for each base / currency pair we want to trade
import os
import sys
import importlib
from trader.lib.struct.Order import Order
from trader.lib.struct.Exchange import Exchange
from trader.OrderHandler import OrderHandler
#from trader.KlinesDB import KlinesDB
from trader.lib.TraderMessageHandler import TraderMessage, TraderMessageHandler
from datetime import datetime
import time


def select_strategy(sname, client, base='BTC', currency='USD', account_handler=None, order_handler=None,
                    asset_info=None, config=None, logger=None):
    strategy = None
    try:
        # load strategy dynamically using importlib
        mod = importlib.import_module("trader.strategy.{}".format(sname))
        strategy = getattr(mod, sname)
    except ImportError:
            print("Unable to load strategy {}".format(sname))
            sys.exit(-1)

    if not strategy:
        return None

    return strategy(client,
                    base,
                    currency,
                    account_handler,
                    order_handler=order_handler,
                    asset_info=asset_info,
                    config=config,
                    logger=logger)


# handle incoming websocket messages for all symbols, and create new tradepairs
# for those that do not yet exist
class MultiTrader(object):
    def __init__(self, client, assets_info=None, simulate=False, accnt=None, logger=None,
                 config=None):
        self.trade_pairs = {}
        self.accounts = {}
        self.client = client
        self.config = config
        self.logger = logger

        self.simulate = self.config.get('simulate')
        self.root_path = self.config.get('path')
        self.db_path = self.config.get('db_path')
        self.store_trades = self.config.get('store_trades')
        self.strategy_name = self.config.get('strategy')
        self.signal_names = [self.config.get('signals')]

        # sets what currency to use when calculating trade profits
        self.trader_profit_mode = self.config.get('trader_profit_mode')
        self.accnt = accnt

        self.logger.info("Setting trader profit mode to {}".format(self.trader_profit_mode))
        self.accnt.set_trader_profit_mode(self.trader_profit_mode)

        self.assets_info = assets_info

        self.tickers = None
        self.msg_handler = TraderMessageHandler()

        self.notify = None
        self.current_ts = 0
        self.last_ts = 0
        self.check_ts_min = self.accnt.seconds_to_ts(60)   # 1 minute
        self.check_ts = self.accnt.seconds_to_ts(3600)     # 1 hour
        self.check_count = 0
        self.stopped = False
        self.running = True
        self.order_handler = OrderHandler(self.accnt, self.msg_handler, self.logger, self.store_trades)

        sigstr = None

        if self.signal_names:
            sigstr = ','.join(self.signal_names)

        if self.simulate:
            run_type = "simulation"
        else:
            run_type = "live"
            # purge trades from TraderDB which have been sold
            self.accnt.load_exchange_info()
            self.purge_trade_db()

        #if self.accnt.get_trader_mode() == Exchange.TRADER_MODE_REALTIME:
        self.logger.info("Running MultiTrade {} strategy: {} signal(s): {}".format(run_type,
                                                                                   self.strategy_name,
                                                                                   sigstr))

    # close() called when exiting MultiTrader
    def close(self):
        for trade_pair in self.trade_pairs.values():
            trade_pair.close()

    # create new trade pair handler and select strategy
    def add_trade_pair(self, symbol, price=0):
        base_name, currency_name = self.accnt.split_symbol(symbol)

        if not base_name or not currency_name: return None

        # can determine if asset is disabled from hourly klines, so for now don't check if asset is disabled
        if not self.simulate and not self.use_hourly_klines:
            if not self.accnt.is_asset_available(base_name):
                # if an asset has deposit disabled, means its probably suspended
                # or de-listed so DO NOT trade this coin
                self.logger.info("Asset {} disabled".format(base_name))
                return None

        asset_info = self.accnt.get_asset_info_dict(symbol)
        if not self.simulate and not asset_info:
            self.logger.info("No asset info for {}".format(symbol))
            return None

        base_min_size = 0

        trade_pair = select_strategy(self.strategy_name,
                                     self.client,
                                     base_name,
                                     currency_name,
                                     account_handler=self.accnt,
                                     order_handler=self.order_handler,
                                     asset_info=self.accnt.get_asset_info(base=base_name, currency=currency_name),
                                     config=self.config,
                                     logger=self.logger)

        self.trade_pairs[symbol] = trade_pair

        if not self.simulate and self.order_handler.trader_db:
            # if balance of coin is less than base_min_size, remove from trade db
            balance = self.accnt.round_base(float(self.accnt.get_asset_balance(base_name)['balance']))
            if balance >= base_min_size:
                self.order_handler.trade_db_load_symbol(symbol, trade_pair)
        return trade_pair

    def update_initial_currency(self, total=0.0):
        self.order_handler.update_initial_currency(total)

    def get_stored_trades(self):
        return self.order_handler.get_stored_trades()

    # check if trader exists
    def trader_exists(self, symbol):
        try:
            result = self.trade_pairs[symbol]
        except KeyError:
            return False
        return True

    # get existing trader, or create new if it doesn't exist
    def get_trader(self, symbol, price):
        try:
            result = self.trade_pairs[symbol]
        except KeyError:
            result = self.add_trade_pair(symbol, price)
        return result

    # process market update message
    def process_market_message(self, msg):
        kline = msg.kline
        self.current_ts = kline.ts

        # keep track of all current price values for all symbols being processed
        self.accnt.update_ticker(kline.symbol, kline.close, kline.ts)

        symbol_trader = self.get_trader(kline.symbol, kline.close)
        if not symbol_trader:
            return None

        # compute current total percent profit, and update info in strategy
        tpprofit = self.order_handler.get_total_percent_profit()
        if tpprofit != 0:
            symbol_trader.update_total_percent_profit(tpprofit)

        # print alive check message once every hour
        if not self.accnt.simulate:
            if self.last_ts == 0 and self.current_ts != 0:
                self.last_ts = self.current_ts
            elif self.current_ts != 0:
                if (self.current_ts - self.last_ts) > self.check_ts:
                    self.accnt.get_account_balances()

                    self.accnt.load_exchange_info()

                    self.last_ts = self.current_ts
                    timestr = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    self.logger.info("MultiTrader running {}".format(timestr))

                    # purge trades from TraderDB which have been sold
                    self.purge_trade_db()

        symbol_trader.run_update(msg)

        self.order_handler.stored_trades_update(kline)
        self.order_handler.process_limit_order(kline)

        # handle incoming messages
        self.order_handler.process_order_messages()

        if self.accnt.simulate:
            return symbol_trader
        return None

    # purge trades from TraderDB which have been sold
    def purge_trade_db(self):
        trades = self.order_handler.trader_db.get_all_trades()
        for trade in trades:
            symbol = trade['symbol']
            sigid = trade['sigid']
            price = trade['price']
            qty = trade['qty']
            base = self.accnt.get_symbol_base(symbol)
            if not base:
                continue
            asset_info = self.accnt.get_asset_info_dict(symbol)
            if not asset_info:
                continue
            try:
                base_min_size = float(asset_info['base_step_size'])
                min_notional = float(asset_info['minNotional'])
            except (KeyError, TypeError):
                continue

            if min_notional > base_min_size:
                base_min_size = min_notional

            # if balance is less than minimum balance, then remove from trade db and send sell complete
            balance = self.accnt.round_base(float(self.accnt.get_asset_balance(base)['balance']))
            if balance < base_min_size:
                self.logger.info("Removing {} from trade db".format(symbol))
                self.order_handler.trader_db.remove_trade(symbol, sigid)
                self.order_handler.remove_open_order(symbol)
                self.order_handler.send_sell_complete(symbol, price, qty, price, sigid, order_type=Order.TYPE_MARKET)


    # process message from user event socket
    # cmd: NEW, PARTIALLY_FILLED, FILLED, CANCELED
    # types: MARKET, LIMIT, STOP_LOSS_LIMIT
    # side: BUY, SELL
    # other fields: price, size
    def process_user_message(self, msg):
        if self.last_ts == 0 or self.current_ts == 0:
            return

        order_update = self.accnt.parse_order_update(msg)

        if order_update.msg_status == TraderMessage.MSG_SELL_COMPLETE:

            o = self.order_handler.get_open_order(order_update.symbol)
            if o:
                self.logger.info("process_user_message({}) SELL_COMPLETE".format(o.symbol))
                self.accnt.get_account_balances()
                self.order_handler.send_sell_complete(o.symbol, o.price, o.size, o.buy_price, o.sig_id,
                                                      order_type=order_update.msg_type)
                self.order_handler.trader_db.remove_trade(o.symbol, o.sig_id)
                self.order_handler.remove_open_order(o.symbol)
            elif order_update.msg_type != Order.TYPE_MARKET:
                # order placed by user
                o = order_update
                self.logger.info("process_user_message({}) MANUAL_SELL_COMPLETE".format(o.symbol))
                self.accnt.get_account_balances()
                self.order_handler.send_sell_complete(o.symbol,
                                                      o.price,
                                                      o.size,
                                                      buy_price=0,
                                                      sig_id=0,
                                                      order_type=order_update.msg_type)
                self.order_handler.trader_db.remove_trade(o.symbol, 0)

        elif order_update.msg_status == TraderMessage.MSG_SELL_FAILED:
            o = self.order_handler.get_open_order(order_update.symbol)
            if o:
                self.logger.info("process_user_message({}) SELL_FAILED".format(o.symbol))
                self.accnt.get_account_balances()
                self.order_handler.send_sell_failed(o.symbol, o.price, o.size, o.buy_price, o.sig_id,
                                                    order_type=order_update.msg_type)
                self.order_handler.trader_db.remove_trade(o.symbol, o.sig_id)
                self.order_handler.remove_open_order(o.symbol)

        if (self.current_ts - self.last_ts) > self.check_ts_min:
            self.accnt.get_account_balances()
            self.last_ts = self.current_ts
            timestr = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            self.logger.info("MultiTrader running {}".format(timestr))
