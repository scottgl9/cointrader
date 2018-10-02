# OrderHandler: order handler for MultiTrader
from trader.lib.Message import Message
from trader.lib.Order import Order
from trader.notify.Email import Email
from trader.lib.TraderDB import TraderDB
import time
import os

class OrderHandler(object):
    def __init__(self, accnt, msg_handler, logger):
        self.accnt = accnt
        self.msg_handler = msg_handler
        self.logger = logger
        self.open_orders = {}
        self.trader_db = None
        self.tickers = None
        if not self.accnt.simulate:
            self.trade_db_init("trade.db")
            self.notify = Email()
            self.accnt.get_account_balances()
            self.initial_btc = self.accnt.get_total_btc_value()
        else:
            self.initial_btc = self.accnt.get_asset_balance(asset='BTC')['balance']

        self.logger.info("Initial BTC value = {}".format(self.initial_btc))


    def trade_db_init(self, filename):
        if self.accnt.simulate:
            return

        if os.path.exists(filename):
            self.trader_db = TraderDB(filename, logger=self.logger)
            self.trader_db.connect()
            self.logger.info("{} already exists, restoring open trades...".format(filename))
        else:
            # create database which keeps track of buy trades (not sold), so can reload trades
            self.trader_db = TraderDB(filename, logger=self.logger)
            self.trader_db.connect()
            self.logger.info("created {} to track trades".format(filename))


    def trade_db_load_symbol(self, symbol, trade_pair):
        trades = self.trader_db.get_trades(symbol)
        if len(trades) == 0:
            return

        for trade in trades:
            if trade_pair:
                trade_pair.set_buy_price_size(buy_price=trade['price'], buy_size=trade['qty'], sig_id=trade['sigid'])


    def update_tickers(self, tickers):
        self.tickers = tickers


    def process_order_messages(self):
        # handle incoming messages
        if not self.msg_handler.empty():
            for msg in self.msg_handler.get_messages_by_dst_id(Message.ID_MULTI):
                if msg.is_read():
                    continue
                if msg.cmd == Message.MSG_MARKET_BUY:
                    self.place_buy_market_order(msg.src_id, msg.price, msg.size, msg.sig_id)
                    msg.mark_read()
                elif msg.cmd == Message.MSG_MARKET_SELL:
                    self.place_sell_market_order(msg.src_id, msg.price, msg.size, msg.buy_price, msg.sig_id)
                    msg.mark_read()
                elif msg.cmd == Message.MSG_LIMIT_BUY:
                    self.place_buy_limit_order(msg.src_id, msg.price, msg.size)
                    msg.mark_read()
                elif msg.cmd == Message.MSG_LIMIT_SELL:
                    self.place_sell_limit_order(msg.src_id, msg.price, msg.size, msg.buy_price)
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
        if msg['s'] not in self.open_orders.keys():
            return

        order = self.open_orders[msg['s']]
        close = float(msg['c'])
        if ((order.type == Message.MSG_STOP_LOSS_BUY and close >= order.price) or
            (order.type == Message.MSG_LIMIT_BUY and close <= order.price)):
            bought = False
            if self.accnt.simulate:
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
        elif ((order.type == Message.MSG_STOP_LOSS_SELL and close <= order.price) or
              (order.type == Message.MSG_LIMIT_SELL and close >= order.price)):
            sold = False
            if self.accnt.simulate:
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


    def place_buy_limit_order(self, ticker_id, price, size):
        if ticker_id in self.open_orders.keys():
            return

        result = self.accnt.buy_limit(price=price, size=size, ticker_id=ticker_id)
        if not self.accnt.simulate:
            self.logger.info(result)

        order = Order(symbol=ticker_id, price=price, size=size, type=Message.MSG_LIMIT_BUY)
        self.open_orders[ticker_id] = order


    def place_sell_limit_order(self, ticker_id, price, size, buy_price):
        if ticker_id in self.open_orders.keys():
            return

        result = self.accnt.sell_limit(price=price, size=size, ticker_id=ticker_id)
        if not self.accnt.simulate:
            self.logger.info(result)

        order = Order(symbol=ticker_id, price=price, size=size, buy_price=buy_price, type=Message.MSG_LIMIT_SELL)
        self.open_orders[ticker_id] = order


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


    # {u'orderId': 38614135, u'clientOrderId': u'S0FDkNNluyHgdfZt44Ktty', u'origQty': u'0.24000000', u'fills': [{u'commission': u'0.00015000', u'price': u'0.04514300',
    # u'commissionAsset': u'BNB', u'tradeId': 8948934, u'qty': u'0.20000000'}, {u'commission': u'0.00003000', u'price': u'0.04514400', u'commissionAsset': u'BNB', u'tradeId': 8948935,
    # u'qty': u'0.04000000'}], u'symbol': u'BNBETH', u'side': u'BUY', u'timeInForce': u'GTC', u'status': u'FILLED', u'transactTime': 1536316266040, u'type': u'MARKET', u'price': u'0.00000000',
    #  u'executedQty': u'0.24000000', u'cummulativeQuoteQty': u'0.01083436'}
    def place_buy_market_order(self, ticker_id, price, size, sig_id):
        result = self.accnt.buy_market(size=size, price=price, ticker_id=ticker_id)
        if not self.accnt.simulate:
            self.logger.info(result)

        if not self.accnt.simulate and not result:
            self.msg_handler.buy_failed(ticker_id, price, size, sig_id)
            return

        if self.accnt.simulate:
            self.buy_order_id = None
            message = "buy({}, {}, {}) @ {}".format(sig_id, ticker_id, size, price)
            self.logger.info(message)
        elif ('status' in result and result['status'] == 'FILLED'):
            if 'orderId' not in result:
                self.logger.warn("orderId not found for {}".format(ticker_id))
                return
            orderid = result['orderId']
            self.buy_order_id = orderid
            message = "buy({}, {}, {}) @ {}".format(sig_id, ticker_id, size, price)
            self.logger.info(message)
            self.accnt.get_account_balances()
            # add to trader db for tracking
            self.trader_db.insert_trade(int(time.time()), ticker_id, price, size, sig_id)
            if self.notify:
                self.notify.send(subject="MultiTrader", text=message)
        else:
            self.msg_handler.buy_failed(ticker_id, price, size, sig_id)


    def place_sell_market_order(self, ticker_id, price, size, buy_price, sig_id):
        # if available balance on coin changed after buy, update available size
        if not self.accnt.simulate:
            self.accnt.get_account_balances()
            base, currency = self.accnt.split_ticker_id(ticker_id)
            available_size = self.accnt.round_base(self.accnt.get_asset_balance(base)['available'])
            if available_size == 0:
                self.trader_db.remove_trade(ticker_id, sig_id)
                self.msg_handler.sell_failed(ticker_id, price, size, buy_price, sig_id)
                return
            #if available_size < size:
            #    return

        result = self.accnt.sell_market(size=size, price=price, ticker_id=ticker_id)

        if not self.accnt.simulate:
            self.logger.info(result)

        if not self.accnt.simulate and not result:
            self.msg_handler.sell_failed(ticker_id, price, size, buy_price, sig_id)
            return

        message=''
        if self.accnt.simulate or ('status' in result and result['status'] == 'FILLED'):
            pprofit = 100.0 * (price - buy_price) / buy_price
            if self.tickers and self.initial_btc != 0:
                current_btc = self.accnt.get_total_btc_value(self.tickers)
                tpprofit = 100.0 * (current_btc - self.initial_btc) / self.initial_btc
                message = "sell({}, {}, {}) @ {} (bought @ {}, {}%)\t{}%".format(sig_id,
                                                                         ticker_id,
                                                                         size,
                                                                         price,
                                                                         buy_price,
                                                                         round(pprofit, 2),
                                                                         round(tpprofit, 2))
            else:
                message = "sell({}, {}, {}) @ {} (bought @ {}, {}%)".format(sig_id,
                                                                    ticker_id,
                                                                    size,
                                                                    price,
                                                                    buy_price,
                                                                    round(pprofit, 2))

            self.logger.info(message)
            if not self.accnt.simulate:
                self.accnt.get_account_balances()
                # remove from trade db since it has been sold
                self.trader_db.remove_trade(ticker_id, sig_id)
                if self.notify:
                    self.notify.send(subject="MultiTrader", text=message)

        elif not self.accnt.simulate:
            self.msg_handler.sell_failed(ticker_id, price, size, buy_price, sig_id)
