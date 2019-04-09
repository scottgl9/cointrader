from trader.lib.Message import Message
from trader.lib.Order import Order
from trader.notify.Email import Email
from trader.lib.TraderDB import TraderDB
from trader.TradeBalanceHandler import TradeBalanceHandler
import time
import os

class OrderLimitHandler(object):
    def __init__(self, accnt, msg_handler, logger):
        self.accnt = accnt
        self.msg_handler = msg_handler
        self.logger = logger
        self.open_orders = {}

    def get_open_order(self, symbol):
        try:
            result = self.open_orders[symbol]
            return result
        except KeyError:
            return None

    def add_open_order(self, symbol, order):
        try:
            result = self.open_orders[symbol]
            if result:
                return False
        except KeyError:
            pass

        self.open_orders[symbol] = order
        return True

    def remove_open_order(self, symbol):
        try:
            del self.open_orders[symbol]
            return True
        except KeyError:
            return False

    def process_limit_order(self, kline):
        if kline.symbol not in self.open_orders.keys():
            return

        order = self.open_orders[kline.symbol]
        close = kline.close
        if ((order.type == Message.MSG_STOP_LOSS_BUY and close > order.price) or
            (order.type == Message.MSG_STOP_LOSS_LIMIT_BUY and close > order.price) or
            (order.type == Message.MSG_TAKE_PROFIT_BUY and close > order.price) or
            (order.type == Message.MSG_PROFIT_LIMIT_BUY and close > order.price) or
            (order.type == Message.MSG_LIMIT_BUY and close < order.price)):

            # convert Message.MSG_* to Message.TYPE_* (ex. Message.MSG_STOP_LOSS_BUY -> Message.TYPE_STOP_LOSS)
            order_type = Message.get_type_from_cmd(order.type)

            if self.accnt.simulate:
                self.send_buy_complete(ticker_id=kline.symbol,
                                              sig_id=order.sig_id,
                                              price=order.price,
                                              size=order.size,
                                              order_type=order_type)
                self.accnt.buy_limit_complete(order.price, order.size, order.symbol)
                self.remove_open_order(kline.symbol)
            else:
                result = self.accnt.get_order(order_id=order.orderid, ticker_id=order.symbol)
                if ('status' in result and result['status'] == 'FILLED'):
                    self.send_buy_complete(ticker_id=kline.symbol,
                                           sig_id=order.sig_id,
                                           price=order.price,
                                           size=order.size,
                                           order_type=order_type)
                    self.accnt.buy_limit_complete(order.price, order.size, order.symbol)
                    self.send_buy_complete(order.symbol, order.price, order.size,
                                            order.sig_id, order_type=order_type)
                    self.remove_open_order(kline.symbol)
        elif ((order.type == Message.MSG_STOP_LOSS_LIMIT_SELL and close < order.price) or
              (order.type == Message.MSG_STOP_LOSS_SELL and close < order.price) or
              (order.type == Message.MSG_TAKE_PROFIT_SELL and close < order.price) or
              (order.type == Message.MSG_PROFIT_LIMIT_SELL and close < order.price) or
              (order.type == Message.MSG_LIMIT_SELL and close > order.price)):

            # convert Message.MSG_* to Message.TYPE_* (ex. Message.MSG_STOP_LOSS_SELL -> Message.TYPE_STOP_LOSS)
            order_type = Message.get_type_from_cmd(order.type)

            if self.accnt.simulate:
                self.accnt.sell_limit_complete(order.price, order.size, order.symbol)
                self.send_sell_complete(order.symbol, order.price, order.size, order.buy_price,
                                        order.sig_id, order_type=order_type)
                self.remove_open_order(kline.symbol)
            else:
                result = self.accnt.get_order(order_id=order.orderid, ticker_id=order.symbol)
                if ('status' in result and result['status'] == 'FILLED'):
                    self.accnt.sell_limit_complete(order.price, order.size, order.symbol)
                    self.send_sell_complete(order.symbol, order.price, order.size, order.buy_price,
                                            order.sig_id, order_type=order_type)
                    self.remove_open_order(kline.symbol)


    def send_buy_failed(self, ticker_id, price, size, sig_id, order_type):
        return self.msg_handler.buy_failed(ticker_id, price, size, sig_id, order_type=order_type)


    def send_sell_failed(self, ticker_id, price, size, buy_price, sig_id, order_type):
        return self.msg_handler.sell_failed(ticker_id, price, size, buy_price, sig_id, order_type=order_type)


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
        if self.accnt.total_btc_available() and self.accnt.initial_btc:
            current_btc = self.accnt.get_total_btc_value()
            tpprofit = 100.0 * (current_btc - self.accnt.initial_btc) / self.accnt.initial_btc
            self.accnt.set_total_percent_profit(tpprofit)
            message = "{}({}, {}, {}) @ {} (bought @ {}, {}%)\t{}%".format(sell_type,
                                                                           sig_id,
                                                                           ticker_id,
                                                                           size,
                                                                           price,
                                                                           buy_price,
                                                                           round(pprofit, 2),
                                                                           round(tpprofit, 2))
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
