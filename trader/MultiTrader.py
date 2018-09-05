# handle multiple TraiePairs, one for each base / currency we want to trade
from trader.account.AccountBinance import AccountBinance
from trader.RankManager import RankManager
from trader.strategy import *
from trader.TradePair import TradePair
from trader.indicator.SMA import SMA
from trader.lib.MessageHandler import Message, MessageHandler
from trader.lib.Order import Order
from trader.notify.Email import Email
import sqlite3
import os.path
import sys
import time
from trader.TraderDB import TraderDB

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
    def __init__(self, client, strategy_name='', assets_info=None, volumes=None,
                 account_name='Binance', simulate=False, accnt=None, ranking=False, logger=None):
        self.trade_pairs = {}
        self.accounts = {}
        self.client = client
        self.simulate = simulate
        self.strategy_name = strategy_name
        if accnt:
            self.accnt = accnt
        else:
            self.accnt = AccountBinance(self.client, simulation=simulate)  # , account_name='Binance')
        self.assets_info = assets_info
        self.volumes = volumes
        self.rank = RankManager()
        self.ranking = ranking
        self.roc_ema = SMA(50)
        self.tickers = None
        self.msg_handler = MessageHandler()
        self.logger = logger
        self.notify = None
        self.current_ts = 0
        self.last_ts = 0
        self.check_ts = 3600 * 1000 * 4
        self.open_orders = {}

        if not self.simulate:
            self.trade_db_init("trade.db")
            self.notify = Email()

        self.initial_btc = self.accnt.get_asset_balance(asset='BTC')['balance']

        if self.simulate:
            self.logger.info("Running MultiTrader as simulation with strategy {}".format(self.strategy_name))
        else:
            self.logger.info("Running MultiTrade live with strategy {}".format(self.strategy_name))


    def trade_db_init(self, filename):
        if os.path.exists(filename):
            self.trader_db = TraderDB(filename)
            self.trader_db.connect()
            self.logger.info("{} already exists, restoring open trades...".format(filename))
            #self.trade_db_load()
        else:
            # create database which keeps track of buy trades (not sold), so can reload trades
            self.trader_db = TraderDB(filename)
            self.trader_db.connect()
            self.logger.info("created {} to track trades".format(filename))


    # load computed buy orders from the db which have not yet been sold, and load into traid pair strategy
    def trade_db_load(self):
        for trade in self.trader_db.load_trades():
            if trade['symbol'] not in self.trade_pairs.keys():
                self.add_trade_pair(trade['symbol'])

            symbol_trader = self.trade_pairs[trade['symbol']]
            symbol_trader.set_buy_price_size(buy_price=trade['price'], buy_size=trade['qty'])


    # create new tradepair handler and select strategy
    def add_trade_pair(self, symbol):
        base_min_size = 0.0
        quote_increment = 0.0
        if symbol in self.assets_info.keys():
            base_min_size = float(self.assets_info[symbol]['minQty'])
            quote_increment = float(self.assets_info[symbol]['tickSize'])

        base_name, currency_name = split_symbol(symbol)
        if not base_name or not currency_name: return

        strategy = select_strategy(self.strategy_name,
                                   self.client,
                                   base_name,
                                   currency_name,
                                   account_handler=self.accnt,
                                   base_min_size=base_min_size,
                                   tick_size=quote_increment,
                                   rank=self.rank,
                                   logger=self.logger)

        trade_pair = TradePair(self.client, self.accnt, strategy, base_name, currency_name)

        self.trade_pairs[symbol] = trade_pair


    def get_trader(self, symbol):
        if symbol not in self.trade_pairs.keys():
            self.add_trade_pair(symbol)
        return self.trade_pairs[symbol]


    def process_message(self, msg):
        if len(msg) == 0: return

        if not isinstance(msg, list):
            if 's' not in msg.keys(): return

            if msg['s'] not in self.trade_pairs.keys():
                self.add_trade_pair(msg['s'])

            if msg['s'] not in self.trade_pairs.keys(): return

            symbol_trader = self.trade_pairs[msg['s']]
            if self.ranking and symbol_trader.last_close != 0.0:
                close = float(msg['c'])
                roc = 100.0 * (close / symbol_trader.last_close - 1)
                self.rank.update(msg['s'], self.roc_ema.update(roc))
            if 'E' in msg:
                self.current_ts = msg['E']
            symbol_trader.update_tickers(self.tickers)
            symbol_trader.run_update(msg)

            if msg['s'] in self.open_orders.keys():
                self.process_limit_order(msg)
        else:
            for part in msg:
                if 's' not in part.keys(): continue

                if part['s'] not in self.trade_pairs.keys():
                    self.add_trade_pair(part['s'])

                if part['s'] not in self.trade_pairs.keys(): continue
                #if self.volumes and part['s'] not in self.volumes.keys(): continue

                symbol_trader = self.trade_pairs[part['s']]
                if self.ranking and symbol_trader.last_close != 0.0:
                    print(part)
                    close = float(part['c'])
                    roc = 100.0 * (close / symbol_trader.last_close - 1)
                    self.rank.update(part['s'], self.roc_ema.update(roc))
                if 'E' in part:
                    self.current_ts = part['E']
                symbol_trader.update_tickers(self.tickers)
                symbol_trader.run_update(part)

                if part['s'] in self.open_orders.keys():
                    self.process_limit_order(part)

        # print alive check message once every 4 hours
        if not self.accnt.simulate:
            if self.last_ts == 0 and self.current_ts != 0:
                self.last_ts = self.current_ts
            elif self.current_ts != 0:
                if (self.current_ts - self.last_ts) > self.check_ts:
                    self.logger.info("MultiTrader still running...")
                    self.logger.info(self.accnt.get_account_balances())
                    self.last_ts = self.current_ts

        # handle incoming messages
        if not self.msg_handler.empty():
            for msg in self.msg_handler.get_messages_by_dst_id(Message.ID_MULTI):
                if msg.cmd == Message.MSG_MARKET_BUY:
                    self.place_buy_market_order(msg.src_id, msg.price, msg.size)
                    msg.mark_read()
                elif msg.cmd == Message.MSG_MARKET_SELL:
                    self.place_sell_market_order(msg.src_id, msg.price, msg.size, msg.buy_price)
                    msg.mark_read()
                elif msg.cmd == Message.MSG_MARKET_SELL_ALL:
                    self.sell_market_all()
                    msg.mark_read()
                elif msg.cmd == Message.MSG_STOP_LOSS_BUY:
                    self.place_buy_stop_loss_order(msg.src_id, msg.price, msg.size)
                    msg.mark_read()
                elif msg.cmd == Message.MSG_STOP_LOSS_SELL:
                    self.place_sell_stop_loss_order(msg.src_id, msg.price, msg.size, msg.buy_price)
                    msg.mark_read()
                elif msg.cmd == Message.MSG_BUY_REPLACE:
                    self.replace_buy_order(msg.src_id, msg.price, msg.size)
                    msg.mark_read()
                elif msg.cmd == Message.MSG_SELL_REPLACE:
                    self.replace_sell_order(msg.src_id, msg.price, msg.size, msg.buy_price)
                    msg.mark_read()
            self.msg_handler.clear_read()

    def process_limit_order(self, msg):
        order = self.open_orders[msg['s']]
        close = float(msg['c'])
        if order.type == Message.MSG_STOP_LOSS_BUY and close >= order.price:
            bought = False
            if self.simulate:
                self.msg_handler.add_message(Message.ID_MULTI, msg['s'], Message.MSG_BUY_COMPLETE, order.price, order.size)
                self.accnt.buy_limit_complete(order.price, order.size, order.symbol)
                bought = True
            else:
                result = self.accnt.get_order(order_id=order.orderid, ticker_id=order.symbol)
                if ('status' in result and result['status'] == 'FILLED'):
                    self.msg_handler.add_message(Message.ID_MULTI, msg['s'], Message.MSG_BUY_COMPLETE, order.price, order.size)
                    self.accnt.buy_limit_complete(order.price, order.size, order.symbol)
                    bought = True
            if bought:
                self.logger.info("buy({}, {}) @ {}".format(order.symbol, order.size, order.price))
                del self.open_orders[msg['s']]
        elif order.type == Message.MSG_STOP_LOSS_SELL and close <= order.price:
            sold = False
            if self.simulate:
                self.msg_handler.add_message(Message.ID_MULTI, msg['s'], Message.MSG_SELL_COMPLETE, order.price, order.size)
                self.accnt.sell_limit_complete(order.price, order.size, order.symbol)
                sold = True
            else:
                result = self.accnt.get_order(order_id=order.orderid, ticker_id=order.symbol)
                if ('status' in result and result['status'] == 'FILLED'):
                    self.msg_handler.add_message(Message.ID_MULTI, msg['s'], Message.MSG_SELL_COMPLETE, order.price, order.size)
                    self.accnt.sell_limit_complete(order.price, order.size, order.symbol)
                    sold = True

            if not sold:
                return

            pprofit = 100.0 * (order.price - order.buy_price) / order.buy_price

            if self.tickers and self.initial_btc != 0:
                current_btc = self.accnt.get_total_btc_value(self.tickers)
                tpprofit = 100.0 * (current_btc - self.initial_btc) / self.initial_btc
                message = "sell({}, {}) @ {} (bought @ {}, {}%)\t{}%".format(order.symbol,
                                                                         order.size,
                                                                         order.price,
                                                                         order.buy_price,
                                                                         round(pprofit, 2),
                                                                         round(tpprofit, 2))
            else:
                message = "sell({}, {}) @ {} (bought @ {}, {}%)".format(order.symbol,
                                                                    order.size,
                                                                    order.price,
                                                                    order.buy_price,
                                                                    round(pprofit, 2))

            self.logger.info(message)
            del self.open_orders[msg['s']]


    def replace_buy_order(self, ticker_id, price, size):
        if ticker_id not in self.open_orders.keys():
            return

        order = self.open_orders[ticker_id]
        orderid = order.orderid
        if not self.accnt.simulate:
            result = self.accnt.cancel_order(orderid=orderid)

        del self.open_orders[ticker_id]

        self.place_buy_stop_loss_order(ticker_id, price, size)


    def replace_sell_order(self, ticker_id, price, size, buy_price):
        if ticker_id not in self.open_orders.keys():
            return

        order = self.open_orders[ticker_id]
        orderid = order.orderid
        if not self.accnt.simulate:
            result = self.accnt.cancel_order(orderid=orderid)

        del self.open_orders[ticker_id]

        self.place_sell_stop_loss_order(ticker_id, price, size, buy_price)


    def place_buy_stop_loss_order(self, ticker_id, price, size):
        if ticker_id in self.open_orders.keys():
            return

        result = self.accnt.buy_limit_stop(price=price, size=size, stop_price=price, ticker_id=ticker_id)
        if not self.accnt.simulate:
            self.logger.info(result)

        order = Order(symbol=ticker_id, price=price, size=size, type=Message.MSG_STOP_LOSS_BUY)
        self.open_orders[ticker_id] = order


    def place_sell_stop_loss_order(self, ticker_id, price, size, buy_price):
        if ticker_id in self.open_orders.keys():
            return

        result = self.accnt.sell_limit_stop(price=price, size=size, stop_price=price, ticker_id=ticker_id)
        if not self.accnt.simulate:
            self.logger.info(result)

        order = Order(symbol=ticker_id, price=price, size=size, buy_price=buy_price, type=Message.MSG_STOP_LOSS_SELL)
        self.open_orders[ticker_id] = order


    # sell off everything that was bought
    def sell_market_all(self):
        for trader in self.trade_pairs.values():
            buy_price = trader.strategy.buy_price
            buy_size = trader.strategy.buy_size
            ticker_id = trader.strategy.ticker_id
            if float(buy_price) == 0 or float(buy_size) == 0:
                continue
            self.place_sell_market_order(ticker_id, 0, buy_size, buy_price)
            trader.strategy.buy_price = 0.0
            trader.strategy.buy_size = 0.0
            trader.strategy.buy_order_id = None


    def place_buy_market_order(self, ticker_id, price, size):
        result = self.accnt.buy_market(size=size, price=price, ticker_id=ticker_id)
        if not self.accnt.simulate:
            self.logger.info(result)

        message = "buy({}, {}) @ {}".format(ticker_id, size, price)
        self.logger.info(message)

        if not self.accnt.simulate and not result:
            return

        if self.accnt.simulate or ('status' in result and result['status'] == 'FILLED'):
            self.buy_order_id = None
            if not self.accnt.simulate:
                if 'orderId' not in result:
                    self.logger.warn("orderId not found for {}".format(ticker_id))
                    return
                orderid = result['orderId']
                self.buy_order_id = orderid

        if not self.accnt.simulate:
            self.accnt.get_account_balances()
            if self.notify:
                self.notify.send(subject="MultiTrader", text=message)

        # add to trader db for tracking
        #self.trader_db.insert_trade(int(time.time()), ticker_id, price, size)


    def place_sell_market_order(self, ticker_id, price, size, buy_price):
        result = self.accnt.sell_market(size=size, price=price, ticker_id=ticker_id)
        if not self.accnt.simulate:
            self.logger.info(result)

        if not self.accnt.simulate and not result: return

        message=''
        if self.accnt.simulate or ('status' in result and result['status'] == 'FILLED'):
            pprofit = 100.0 * (price - buy_price) / buy_price
            if self.tickers and self.initial_btc != 0:
                current_btc = self.accnt.get_total_btc_value(self.tickers)
                tpprofit = 100.0 * (current_btc - self.initial_btc) / self.initial_btc
                message = "sell({}, {}) @ {} (bought @ {}, {}%)\t{}%".format(ticker_id,
                                                                         size,
                                                                         price,
                                                                         buy_price,
                                                                         round(pprofit, 2),
                                                                         round(tpprofit, 2))
            else:
                message = "sell({}, {}) @ {} (bought @ {}, {}%)".format(ticker_id,
                                                                    size,
                                                                    price,
                                                                    buy_price,
                                                                    round(pprofit, 2))

            self.logger.info(message)

            if not self.accnt.simulate:
                total_usd, total_btc = self.accnt.get_account_total_value()
                self.logger.info("Total balance USD = {}, BTC={}".format(total_usd, total_btc))
        if not self.accnt.simulate:
            self.accnt.get_account_balances()
            if self.notify:
                self.notify.send(subject="MultiTrader", text=message)

        # remove from trade db since it has been sold
        #self.trader_db.remove_trade(ticker_id)


    def update_tickers(self, tickers):
        self.tickers = tickers
