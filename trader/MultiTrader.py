# handle multiple TraiePairs, one for each base / currency we want to trade
from trader.account.AccountBinance import AccountBinance
from trader.OrderHandler import OrderHandler
from trader.lib.Kline import Kline
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.lib.MessageHandler import Message, MessageHandler
from trader.strategy.global_strategy.global_obv_strategy import global_obv_strategy
from datetime import datetime

from trader.strategy.basic_signal_market_strategy import basic_signal_market_strategy
from trader.strategy.basic_signal_stop_loss_strategy import basic_signal_stop_loss_strategy
from trader.strategy.signal_market_trailing_stop_loss_strategy import signal_market_trailing_stop_loss_strategy
from trader.strategy.null_strategy import null_strategy


def select_strategy(sname, client, base='BTC', currency='USD', account_handler=None, order_handler=None,
                    hourly_klines_handler=None, base_min_size=0.0, tick_size=0.0, asset_info=None, config=None, logger=None):
    strategy = None
    if sname == 'basic_signal_market_strategy': strategy = basic_signal_market_strategy
    elif sname == 'basic_signal_stop_loss_strategy': strategy = basic_signal_stop_loss_strategy
    elif sname == 'signal_market_trailing_stop_loss_strategy': strategy = signal_market_trailing_stop_loss_strategy
    elif sname == 'null_strategy': strategy = null_strategy
    if not strategy:
        return None

    return strategy(client,
                    base,
                    currency,
                    account_handler,
                    order_handler=order_handler,
                    #hourly_klines_handler=hourly_klines_handler,
                    asset_info=asset_info,
                    base_min_size=base_min_size,
                    tick_size=tick_size,
                    config=config,
                    logger=logger)


# handle incoming websocket messages for all symbols, and create new tradepairs
# for those that do not yet exist
class MultiTrader(object):
    def __init__(self, client, assets_info=None, simulate=False, accnt=None, logger=None,
                 global_en=True, config=None):
        self.trade_pairs = {}
        self.accounts = {}
        self.client = client
        self.config = config
        self.logger = logger

        self.simulate = self.config.get('simulate')
        self.store_trades = self.config.get('store_trades')
        self.strategy_name = self.config.get('strategy')
        self.signal_names = [self.config.get('signals')]
        self.hourly_signal_name = self.config.get('hourly_signal')
        self.hourly_klines_db_file = self.config.get('hourly_kline_db_file')
        self.usdt_value_cutoff = float(self.config.get('usdt_value_cutoff'))
        self.use_hourly_klines = self.config.get('use_hourly_klines')

        self.logger.info("Setting USDT value cutoff to {}".format(self.usdt_value_cutoff))

        if accnt:
            self.accnt = accnt
        else:
            self.accnt = AccountBinance(self.client,
                                        simulation=simulate,
                                        logger=logger)
        self.assets_info = assets_info
        self.tickers = None
        self.msg_handler = MessageHandler()
        self.hourly_klines_handler = None
        self.last_hourly_ts = 0

        if self.use_hourly_klines:
            try:
                self.hourly_klines_handler = HourlyKlinesDB(self.accnt, self.hourly_klines_db_file, self.logger)
                self.logger.info("hourly_klines_handler: loaded {}".format(self.hourly_klines_db_file))
            except IOError:
                self.logger.warning("hourly_klines_handler: Failed to load {}".format(self.hourly_klines_db_file))
                self.hourly_klines_handler = None

        if not self.simulate and self.hourly_klines_handler:
            self.logger.info("Updating hourly kline tables in {}...".format(self.hourly_klines_db_file))
            self.last_hourly_ts = self.hourly_klines_handler.update_all_tables()

        self.notify = None
        self.current_ts = 0
        self.last_ts = 0
        self.check_ts_min = self.accnt.seconds_to_ts(60)   # 1 minute
        self.check_ts = self.accnt.seconds_to_ts(3600)     # 1 hour
        self.check_count = 0
        self.stopped = False
        self.running = True
        self.order_handler = OrderHandler(self.accnt, self.msg_handler, self.logger, self.store_trades)
        self.global_strategy = None
        self.global_en = global_en
        if self.global_en:
            self.global_strategy = global_obv_strategy()

        #if not self.simulate and self.accnt.hourly_klines_handler:
        #    self.logger.info("Updating hourly klines in {}...".format(self.hourly_klines_db_file))
        #    self.accnt.hourly_klines_handler.update_all_tables()

        sigstr = None

        if self.signal_names:
            sigstr = ','.join(self.signal_names)

        if self.simulate:
            run_type = "simulation"
        else:
            run_type = "live"

        if sigstr:
            self.logger.info("Running MultiTrade {} strategy {} signal(s) {} hourly signal: {}".format(run_type,
                                                                                                       self.strategy_name,
                                                                                                       sigstr,
                                                                                                       self.hourly_signal_name))
        else:
            self.logger.info("Running MultiTrade {} strategy {}".format(run_type, self.strategy_name))


    # create new tradepair handler and select strategy
    def add_trade_pair(self, symbol, price=0):
        base_name, currency_name = self.accnt.split_symbol(symbol)

        if not base_name or not currency_name: return None

        # if an asset has deposit disabled, means its probably suspended
        # or de-listed so DO NOT trade this coin
        if self.accnt.deposit_asset_disabled(base_name):
            return None

        asset_info = self.accnt.get_asset_info_dict(symbol)
        if not asset_info:
            return None

        # if set to trade BTC only, do not process add trade pair if not BTC currency
        if self.accnt.btc_only() and currency_name != 'BTC':
            return None

        # check USDT value of base by calculating (base_currency) * (currency_usdt)
        # verify that USDT value >= self.usdt_value_cutoff, if less do not buy
        usdt_value = self.accnt.get_usdt_value_symbol(symbol, float(price))
        if usdt_value:
            if usdt_value < self.usdt_value_cutoff:
                return None

        # *FIXME* use AssetInfo class instead
        base_min_size = float(asset_info['stepSize'])
        tick_size = float(asset_info['tickSize'])
        min_notional = float(asset_info['minNotional'])

        if min_notional > base_min_size:
            base_min_size = min_notional

        trade_pair = select_strategy(self.strategy_name,
                                     self.client,
                                     base_name,
                                     currency_name,
                                     account_handler=self.accnt,
                                     order_handler=self.order_handler,
                                     #hourly_klines_handler=self.hourly_klines_handler,
                                     base_min_size=base_min_size,
                                     tick_size=tick_size,
                                     asset_info=self.accnt.get_asset_info(base=base_name, currency=currency_name),
                                     config=self.config,
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

    def get_trader(self, symbol, price):
        try:
            result = self.trade_pairs[symbol]
        except KeyError:
            result = self.add_trade_pair(symbol, price)
        return result

    def process_message(self, kline, cache_db=None):
        self.current_ts = kline.ts

        symbol_trader = self.get_trader(kline.symbol, kline.close)
        if not symbol_trader:
            return None

        # keep track of all current price values for all symbols being processed
        self.accnt.update_ticker(kline.symbol, kline.close, kline.ts)

        # compute current total percent profit, and update info in strategy
        tpprofit = self.order_handler.get_total_percent_profit()
        if tpprofit != 0:
            symbol_trader.update_total_percent_profit(tpprofit)

        # print alive check message once every hour
        if not self.accnt.simulate:
            hourly_klines_handler = symbol_trader.hourly_klines_handler

            if hourly_klines_handler:
                last_hourly_ts = hourly_klines_handler.get_last_update_ts(kline.symbol)
                if last_hourly_ts and (self.current_ts - last_hourly_ts) >= self.accnt.seconds_to_ts(3600 - 1):
                    hourly_ts = self.accnt.get_hourly_ts(self.current_ts)
                    if hourly_ts != last_hourly_ts:
                        hourly_klines_handler.update_table(kline.symbol, end_ts=hourly_ts)
                        if hourly_ts != self.last_hourly_ts:
                            self.logger.info("Updating hourly klines hourly_ts={}".format(hourly_ts))
                            self.last_hourly_ts = hourly_ts
            elif self.last_ts == 0 and self.current_ts != 0:
                self.last_ts = self.current_ts
            elif self.current_ts != 0:
                if (self.current_ts - self.last_ts) > self.check_ts:
                    self.accnt.get_account_balances()

                    # keep asset details up to date
                    self.accnt.load_detail_all_assets()

                    self.last_ts = self.current_ts
                    timestr = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    self.logger.info("MultiTrader running {}".format(timestr))

        symbol_trader.run_update(kline, cache_db=cache_db)

        if self.global_strategy:
            self.global_strategy.run_update(kline)

        self.order_handler.stored_trades_update(kline)
        self.order_handler.process_limit_order(kline)

        # handle incoming messages
        self.order_handler.process_order_messages()

        if self.accnt.simulate:
            return symbol_trader
        return None

    # process message from user event socket
    # cmd: NEW, PARTIALLY_FILLED, FILLED, CANCELED
    # types: MARKET, LIMIT, STOP_LOSS_LIMIT
    # side: BUY, SELL
    # other fields: price, size
    def process_user_message(self, msg):
        if self.last_ts == 0 or self.current_ts == 0:
            return

        order_update = self.accnt.parse_order_update(msg)

        if order_update.msg_status == Message.MSG_SELL_COMPLETE:

            o = self.order_handler.get_open_order(order_update.symbol)
            if o:
                self.logger.info("process_user_message({}) SELL_COMPLETE".format(o.symbol))
                self.accnt.get_account_balances()
                self.order_handler.send_sell_complete(o.symbol, o.price, o.size, o.buy_price, o.sig_id,
                                                      order_type=order_update.msg_type)
                self.order_handler.trader_db.remove_trade(o.symbol, o.sig_id)
                self.order_handler.remove_open_order(o.symbol)
            elif order_update.msg_type != Message.TYPE_MARKET:
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

        elif order_update.msg_status == Message.MSG_SELL_FAILED:
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
