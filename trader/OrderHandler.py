# OrderHandler: order handler for MultiTrader
from trader.lib.Message import Message
from trader.lib.Order import Order
from trader.notify.Email import Email
from trader.lib.TraderDB import TraderDB
from trader.TradeBalanceHandler import TradeBalanceHandler
import time
import os


class OrderHandler(object):
    def __init__(self, accnt, msg_handler, logger, store_trades=False):
        self.accnt = accnt
        self.msg_handler = msg_handler
        self.logger = logger
        self.open_orders = {}
        self.trader_db = None
        self.store_trades = store_trades
        self.trades = {}
        self.counters = {}
        self.buy_disabled = False
        self.trade_balance_handler = TradeBalanceHandler(self.accnt, logger=logger)
        # total percent profit
        self.tpprofit = 0

        if not self.accnt.simulate:
            self.trade_db_init("trade.db")
            self.notify = Email()

        self.initial_btc = 0
        self.update_initial_btc()
        self.actual_initial_btc = self.initial_btc

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


    def update_initial_btc(self):
        self.logger.info("Resetting initial BTC...")
        if not self.accnt.simulate:
            self.accnt.get_account_balances()
            self.initial_btc = self.accnt.get_account_total_btc_value()
        else:
            self.initial_btc = self.accnt.get_total_btc_value()


    def get_stored_trades(self):
        return self.trades


    def get_total_percent_profit(self):
        result = self.tpprofit
        return result


    def process_order_messages(self):
        received = False
        # handle incoming messages
        if not self.msg_handler.empty():
            for msg in self.msg_handler.get_messages_by_dst_id(Message.ID_MULTI):
                if msg.is_read():
                    continue
                if msg.cmd == Message.MSG_MARKET_BUY:
                    self.place_buy_market_order(msg)
                    msg.mark_read()
                    received = True
                elif msg.cmd == Message.MSG_MARKET_SELL:
                    self.place_sell_market_order(msg)
                    msg.mark_read()
                    received = True
                elif msg.cmd == Message.MSG_BUY_CANCEL:
                    self.place_cancel_buy_order(msg)
                    msg.mark_read()
                    received = True
                elif msg.cmd == Message.MSG_SELL_CANCEL:
                    self.place_cancel_sell_order(msg)
                    msg.mark_read()
                    received = True
                elif msg.cmd == Message.MSG_LIMIT_BUY:
                    self.place_buy_limit_order(msg)
                    msg.mark_read()
                    received = True
                elif msg.cmd == Message.MSG_LIMIT_SELL:
                    self.place_sell_limit_order(msg)
                    msg.mark_read()
                    received = True
                elif msg.cmd == Message.MSG_STOP_LOSS_BUY:
                    self.place_buy_stop_loss_order(msg)
                    msg.mark_read()
                    received = True
                elif msg.cmd == Message.MSG_STOP_LOSS_SELL:
                    self.place_sell_stop_loss_order(msg)
                    msg.mark_read()
                    received = True
                elif msg.cmd == Message.MSG_BUY_REPLACE:
                    self.replace_buy_order(msg)
                    msg.mark_read()
                    received = True
                elif msg.cmd == Message.MSG_SELL_REPLACE:
                    self.replace_sell_order(msg)
                    msg.mark_read()
                    received = True
                elif msg.cmd == Message.MSG_BUY_DISABLE:
                    self.buy_disabled = True
                    self.logger.info("BUY_DISABLE")
                    msg.mark_read()
                    received = True
                elif msg.cmd == Message.MSG_BUY_ENABLE:
                    self.buy_disabled = False
                    self.logger.info("BUY_ENABLE")
                    msg.mark_read()
                    received = True
            self.msg_handler.clear_read()

        return received


    def process_limit_order(self, kline):
        if self.store_trades:
            if kline.symbol not in self.counters:
                self.counters[kline.symbol] = 1
            else:
                self.counters[kline.symbol] += 1

        if kline.symbol not in self.open_orders.keys():
            return

        order = self.open_orders[kline.symbol]
        close = kline.close
        if ((order.type == Message.MSG_STOP_LOSS_BUY and close > order.price) or
            (order.type == Message.MSG_LIMIT_BUY and close < order.price)):
            bought = False

            order_type = order.type
            if order.type == Message.MSG_STOP_LOSS_BUY:
                order_type = Message.TYPE_STOP_LOSS
            elif order.type == Message.MSG_LIMIT_BUY:
                order_type = Message.TYPE_LIMIT

            if self.accnt.simulate:
                self.send_buy_complete(ticker_id=kline.symbol,
                                              sig_id=order.sig_id,
                                              price=order.price,
                                              size=order.size,
                                              order_type=order_type)
                self.accnt.buy_limit_complete(order.price, order.size, order.symbol)
                bought = True
            else:
                result = self.accnt.get_order(order_id=order.orderid, ticker_id=order.symbol)
                if ('status' in result and result['status'] == 'FILLED'):
                    self.send_buy_complete(ticker_id=kline.symbol,
                                           sig_id=order.sig_id,
                                           price=order.price,
                                           size=order.size,
                                           order_type=order_type)
                    self.accnt.buy_limit_complete(order.price, order.size, order.symbol)
                    bought = True
            if bought:
                self.logger.info("buy({}, {}) @ {}".format(order.symbol, order.size, order.price))
                del self.open_orders[kline.symbol]
        elif ((order.type == Message.MSG_STOP_LOSS_SELL and close < order.price) or
              (order.type == Message.MSG_LIMIT_SELL and close > order.price)):
            sold = False

            order_type = order.type
            if order.type == Message.MSG_STOP_LOSS_SELL:
                order_type = Message.TYPE_STOP_LOSS
            elif order.type == Message.MSG_LIMIT_SELL:
                order_type = Message.TYPE_LIMIT

            if self.accnt.simulate:
                self.accnt.sell_limit_complete(order.price, order.size, order.symbol)
                self.send_sell_complete(order.symbol, order.price, order.size, order.buy_price,
                                        order.sig_id, order_type=order_type)
                sold = True
            else:
                result = self.accnt.get_order(order_id=order.orderid, ticker_id=order.symbol)
                if ('status' in result and result['status'] == 'FILLED'):
                    self.accnt.sell_limit_complete(order.price, order.size, order.symbol)
                    message = self.send_sell_complete(order.symbol, order.price, order.size, order.buy_price,
                                                      order.sig_id, order_type=order_type)
                    sold = True

            if not sold:
                return

            del self.open_orders[kline.symbol]


    def replace_buy_order(self, msg):
        ticker_id = msg.src_id
        price = msg.price
        size = msg.size
        sig_id = msg.sig_id
        if ticker_id not in self.open_orders.keys():
            return

        order = self.open_orders[ticker_id]
        orderid = order.orderid
        if not self.accnt.simulate:
            result = self.accnt.cancel_order(orderid=orderid)
            self.logger.info(result)

        self.logger.info("cancel_buy({}, {}) @ {}".format(order.symbol, order.size, order.price))

        del self.open_orders[ticker_id]

        if order.type == Message.MSG_STOP_LOSS_BUY:
            self.place_buy_stop_loss_order(msg)
        elif order.type == Message.MSG_LIMIT_BUY:
            self.place_buy_limit_order(msg)
        else:
            self.logger.warn("unknown order type {} for {}".format(order.type, ticker_id))


    def replace_sell_order(self, msg):
        ticker_id = msg.src_id
        price = msg.price
        buy_price = msg.buy_price
        size = msg.size
        sig_id = msg.sig_id
        if ticker_id not in self.open_orders.keys():
            return

        order = self.open_orders[ticker_id]
        orderid = order.orderid
        if not self.accnt.simulate:
            result = self.accnt.cancel_order(orderid=orderid)
            self.logger.info(result)

        self.logger.info("cancel_sell({}, {}) @ {} (bought @ {})".format(order.symbol, order.size, order.price, order.buy_price))
        del self.open_orders[ticker_id]

        if order.type == Message.MSG_STOP_LOSS_SELL:
            self.place_sell_stop_loss_order(msg)
        elif order.type == Message.MSG_LIMIT_SELL:
            self.place_sell_limit_order(msg)
        else:
            self.logger.warn("unknown order type {} for {}".format(order.type, ticker_id))


    def place_cancel_buy_order(self, msg):
        ticker_id = msg.src_id
        self.cancel_buy_order(ticker_id)

    def cancel_buy_order(self, symbol):
        if symbol not in self.open_orders.keys():
            return

        order = self.open_orders[symbol]
        if not self.accnt.simulate:
            result = self.accnt.cancel_order(orderid=order.orderid)
            self.logger.info(result)

        self.logger.info("cancel_buy({}, {}) @ {}".format(order.symbol, order.size, order.price))
        del self.open_orders[symbol]

    def place_cancel_sell_order(self, msg):
        ticker_id = msg.src_id
        self.cancel_sell_order(ticker_id)

    def cancel_sell_order(self, symbol):
        if symbol not in self.open_orders.keys():
            return

        order = self.open_orders[symbol]
        if not self.accnt.simulate:
            result = self.accnt.cancel_order(orderid=order.orderid)
            self.logger.info(result)
        else:
            self.accnt.cancel_sell_limit_complete(order.size, symbol)

        self.logger.info("cancel_sell({}, {}) @ {} (bought @ {})".format(order.symbol, order.size, order.price, order.buy_price))
        del self.open_orders[symbol]

    def place_buy_limit_order(self, msg):
        ticker_id = msg.src_id
        price = msg.price
        size = msg.size
        sig_id = msg.sig_id
        if ticker_id in self.open_orders.keys():
            return

        result = self.accnt.buy_limit(price=price, size=size, ticker_id=ticker_id)
        if not self.accnt.simulate:
            self.logger.info(result)

        order = Order(symbol=ticker_id, price=price, size=size, sig_id=sig_id, type=Message.MSG_LIMIT_BUY)
        self.open_orders[ticker_id] = order
        self.logger.info("place_buy_limit({}, {}) @ {}".format(order.symbol, order.size, order.price))


    def place_sell_limit_order(self, msg):
        ticker_id = msg.src_id
        price = msg.price
        buy_price = msg.buy_price
        size = msg.size
        sig_id = msg.sig_id
        if ticker_id in self.open_orders.keys():
            return

        result = self.accnt.sell_limit(price=price, size=size, ticker_id=ticker_id)
        if not self.accnt.simulate:
            self.logger.info(result)

        order = Order(symbol=ticker_id, price=price, size=size, sig_id=sig_id, buy_price=buy_price, type=Message.MSG_LIMIT_SELL)
        self.open_orders[ticker_id] = order
        self.logger.info("place_sell_limit({}, {}) @ {} (bought @ {})".format(order.symbol, order.size, order.price, order.buy_price))


    def place_buy_stop_loss_order(self, msg):
        ticker_id = msg.src_id
        price = msg.price
        size = msg.size
        sig_id = msg.sig_id
        if ticker_id in self.open_orders.keys():
            return

        result = self.accnt.buy_limit_stop(price=price, size=size, stop_price=price, ticker_id=ticker_id)
        if not self.accnt.simulate:
            self.logger.info(result)

        order = Order(symbol=ticker_id, price=price, size=size, sig_id=sig_id, type=Message.MSG_STOP_LOSS_BUY)
        self.open_orders[ticker_id] = order
        self.logger.info("place_buy_stop({}, {}) @ {}".format(order.symbol, order.size, order.price))


    def place_sell_stop_loss_order(self, msg):
        ticker_id = msg.src_id
        price = msg.price
        buy_price = msg.buy_price
        size = msg.size
        sig_id = msg.sig_id
        if ticker_id in self.open_orders.keys():
            return

        result = self.accnt.sell_limit_stop(price=price, size=size, stop_price=price, ticker_id=ticker_id)

        if not self.accnt.simulate:
            self.logger.info(result)

        if not result:
            self.msg_handler.sell_failed(ticker_id, price, size, buy_price, sig_id, order_type=Message.TYPE_STOP_LOSS)
            return

        order = Order(symbol=ticker_id, price=price, size=size, sig_id=sig_id, buy_price=buy_price, type=Message.MSG_STOP_LOSS_SELL)
        self.open_orders[ticker_id] = order

        self.logger.info("place_sell_stop({}, {}) @ {} (bought @ {})".format(order.symbol, order.size, order.price, order.buy_price))


    def place_buy_market_order(self, msg):
        ticker_id = msg.src_id
        price = msg.price
        size = msg.size
        sig_id = msg.sig_id
        base = msg.asset_info.base
        currency = msg.asset_info.currency

        if self.buy_disabled:
            self.msg_handler.buy_failed(ticker_id, price, size, sig_id)
            return

        result = self.accnt.buy_market(size=size, price=price, ticker_id=ticker_id)
        #if not self.accnt.simulate:
        #    self.logger.info(result)

        if not result:
            self.msg_handler.buy_failed(ticker_id, price, size, sig_id)
            return

        if self.accnt.simulate:
            if self.store_trades:
                self.store_trade_json(ticker_id, price, size, 'buy', trade_type=msg.buy_type)
            message = self.send_buy_complete(ticker_id, price, size, sig_id, order_type=Message.TYPE_MARKET)
            self.logger.info(message)
        else:
            order = self.accnt.parse_order_result(result, symbol=ticker_id)
            if isinstance(order, type(None)):
                # parse_order_result() failed to parse json
                message = "order failed: {}".format(str(result))
                self.logger.info(message)
                if self.notify:
                    self.notify.send(subject="MultiTrader", text=message)
                self.msg_handler.buy_failed(ticker_id, price, size, sig_id)
                return
            else:
                self.logger.info("buy_order: {}".format(str(order)))
                # update price from actual sell price for live trading
                if float(order.price) != 0 and float(price) != float(order.price):
                    self.logger.info("update_buy_price({}, {} -> {})".format(ticker_id, price, order.price))
                    price = float(order.price)

                self.accnt.get_account_balances()
                # add to trader db for tracking
                self.trader_db.insert_trade(int(time.time()), ticker_id, price, size, sig_id)
                message = self.send_buy_complete(ticker_id, price, size, sig_id, order_type=Message.TYPE_MARKET)
                self.logger.info(message)
                if self.notify:
                    self.notify.send(subject="MultiTrader", text=message)

        self.trade_balance_handler.update_for_buy(price, size, asset_info=msg.asset_info, symbol=ticker_id)

        if msg.asset_info.is_currency_pair:
            if not self.trade_balance_handler.is_zero_balance(base):
                # send update message to strategy that buy size has changed
                order_size = self.trade_balance_handler.get_balance(base)
                self.msg_handler.order_size_update(ticker_id, price, order_size, sig_id)

            if not self.trade_balance_handler.is_zero_balance(currency):
                # send update message to strategy that buy size has changed
                order_size = self.trade_balance_handler.get_balance(currency)
                symbol = self.trade_balance_handler.get_currency_pair_symbol(currency)
                self.msg_handler.order_size_update(symbol, price, order_size, sig_id)


    def place_sell_market_order(self, msg):
        ticker_id = msg.src_id
        price = msg.price
        buy_price = msg.buy_price
        size = msg.size
        sig_id = msg.sig_id
        base = msg.asset_info.base
        currency = msg.asset_info.currency

        # if available balance on coin changed after buy, update available size
        if not self.accnt.simulate:
            self.accnt.get_account_balances()
            #base, currency = self.accnt.split_ticker_id(ticker_id)
            available_size = self.accnt.round_base(self.accnt.get_asset_balance(base)['available'])
            if available_size == 0:
                self.trader_db.remove_trade(ticker_id, sig_id)
                self.msg_handler.sell_failed(ticker_id, price, size, buy_price, sig_id)
                return
            #if available_size < size:
            #    return

        result = self.accnt.sell_market(size=size, price=price, ticker_id=ticker_id)

        if not result:
            self.msg_handler.sell_failed(ticker_id, price, size, buy_price, sig_id)
            if not self.accnt.simulate:
                # remove from trade db since it failed to be sold
                self.trader_db.remove_trade(ticker_id, sig_id)
            return

        order = self.accnt.parse_order_result(result, symbol=ticker_id)
        if self.accnt.simulate or order:
            if order:
                self.logger.info("sell_order: {}".format(str(order)))
            # update price from actual sell price for live trading
            if not self.accnt.simulate and float(order.price) != 0 and float(price) != float(order.price):
                self.logger.info("update_sell_price({}, {} -> {})".format(ticker_id, price, order.price))
                price = float(order.price)

            if self.store_trades:
                self.store_trade_json(ticker_id, price, size, 'sell', buy_price, trade_type=msg.sell_type)

            if not self.accnt.simulate:
                self.accnt.get_account_balances()
                # remove from trade db since it has been sold
                self.trader_db.remove_trade(ticker_id, sig_id)
                message = self.send_sell_complete(ticker_id, price, size, buy_price, sig_id, order_type=Message.TYPE_MARKET)

                if self.notify:
                    self.notify.send(subject="MultiTrader", text=message)
            else:
                self.send_sell_complete(ticker_id, price, size, buy_price, sig_id, order_type=Message.TYPE_MARKET)
        elif not self.accnt.simulate:
            self.msg_handler.sell_failed(ticker_id, price, size, buy_price, sig_id)
            # remove from trade db since it failed to be sold
            self.trader_db.remove_trade(ticker_id, sig_id)
            return

        self.trade_balance_handler.update_for_sell(price, size, asset_info=msg.asset_info, symbol=ticker_id)

        if msg.asset_info.is_currency_pair:
            if not self.trade_balance_handler.is_zero_balance(base):
                # send update message to strategy that buy size has changed
                order_size = self.trade_balance_handler.get_balance(base)
                self.msg_handler.order_size_update(ticker_id, price, order_size, sig_id)

            if not self.trade_balance_handler.is_zero_balance(currency):
                # send update message to strategy that buy size has changed
                order_size = self.trade_balance_handler.get_balance(currency)
                symbol = self.trade_balance_handler.get_currency_pair_symbol(currency)
                self.msg_handler.order_size_update(symbol, price, order_size, sig_id)

    def send_buy_complete(self, ticker_id, price, size, sig_id, order_type):
        buy_type="buy_unknown"
        if order_type == Message.TYPE_MARKET:
            buy_type = "buy_market"
        elif order_type == Message.TYPE_STOP_LOSS:
            buy_type = "buy_stop_loss"
        elif order_type == Message.TYPE_LIMIT:
            buy_type = "buy_limit"
        elif order_type == Message.MSG_STOP_LOSS_BUY:
            buy_type = "buy_stop_loss"
        elif order_type == Message.MSG_MARKET_BUY:
            buy_type = "buy_market"
        elif order_type == Message.MSG_LIMIT_BUY:
            buy_type = "buy_limit"

        message = "{}({}, {}, {}) @ {}".format(buy_type, sig_id, ticker_id, size, price)
        self.msg_handler.buy_complete(ticker_id, price, size, sig_id, order_type=order_type)
        return message

    def send_sell_complete(self, ticker_id, price, size, buy_price, sig_id, order_type):
        sell_type="sell_unknown"
        if order_type == Message.TYPE_MARKET:
            sell_type = "sell_market"
        elif order_type == Message.TYPE_STOP_LOSS:
            sell_type = "sell_stop_loss"
        elif order_type == Message.TYPE_LIMIT:
            sell_type = "sell_limit"
        elif order_type == Message.MSG_STOP_LOSS_SELL:
            sell_type = "sell_stop_loss"
        elif order_type == Message.MSG_MARKET_SELL:
            sell_type = "sell_market"
        elif order_type == Message.MSG_LIMIT_SELL:
            sell_type = "sell_limit"

        pprofit = 100.0 * (price - buy_price) / buy_price
        if self.accnt.total_btc_available() and self.initial_btc:
            current_btc = self.accnt.get_total_btc_value()
            self.tpprofit = 100.0 * (current_btc - self.initial_btc) / self.initial_btc
            message = "{}({}, {}, {}) @ {} (bought @ {}, {}%)\t{}%".format(sell_type,
                                                                           sig_id,
                                                                           ticker_id,
                                                                           size,
                                                                           price,
                                                                           buy_price,
                                                                           round(pprofit, 2),
                                                                           round(self.tpprofit, 2))
        else:
            message = "{}({}, {}, {}) @ {} (bought @ {}, {}%)".format(sell_type,
                                                                      sig_id,
                                                                      ticker_id,
                                                                      size,
                                                                      price,
                                                                      buy_price,
                                                                      round(pprofit, 2))
        self.logger.info(message)
        self.msg_handler.sell_complete(ticker_id, price, size, buy_price, sig_id, order_type=order_type)
        return message

    # store trade into json trade cache
    def store_trade_json(self, ticker_id, price, size, type, buy_price=0, trade_type=0):
        result = {'symbol': ticker_id,
                  'size': size,
                  'price': price,
                  'type': type,
                  'index': self.counters[ticker_id],
                  'trade_type': trade_type}

        if type == 'sell':
            result['buy_price'] = buy_price

        if ticker_id not in self.trades:
            self.trades[ticker_id] = [result]
        else:
            self.trades[ticker_id].append(result)
