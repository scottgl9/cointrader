from trader.account.AccountBaseTrade import AccountBaseTrade
from trader.account.binance.binance.client import Client, BinanceAPIException
from trader.lib.struct.TraderMessage import TraderMessage
from trader.lib.struct.Order import Order
from trader.lib.struct.OrderUpdate import OrderUpdate


class AccountBinanceTrade(AccountBaseTrade):
    def __init__(self, client, simulation=False, logger=None):
        self.client = client
        self.simulate = simulation
        self.logger = logger

    def buy_market(self, size, price=0.0, ticker_id=None):
        self.logger.info("buy_market({}, {}, {})".format(size, price, ticker_id))
        try:
            result = self.client.order_market_buy(symbol=ticker_id, quantity=size)
        except BinanceAPIException as e:
            self.logger.info(e)
            result = None
        return result

    def sell_market(self, size, price=0.0, ticker_id=None):
        self.logger.info("sell_market({}, {}, {})".format(size, price, ticker_id))
        try:
            result = self.client.order_market_sell(symbol=ticker_id, quantity=size)
        except BinanceAPIException as e:
            self.logger.info(e)
            result = None
        return result

    def buy_limit(self, price, size, ticker_id=None):
        timeInForce = Client.TIME_IN_FORCE_GTC
        return self.client.order_limit_buy(timeInForce=timeInForce, symbol=ticker_id, quantity=size, price=price)

    def sell_limit(self, price, size, ticker_id=None):
        timeInForce = Client.TIME_IN_FORCE_GTC
        return self.client.order_limit_sell(timeInForce=timeInForce, symbol=ticker_id, quantity=size, price=price)

    def get_order(self, order_id, ticker_id):
        return self.client.get_order(orderId=order_id, symbol=ticker_id)

    def get_orders(self, ticker_id=None):
        return self.client.get_open_orders(symbol=ticker_id)

    def cancel_order(self, orderid, ticker_id=None):
        return self.client.cancel_order(symbol=ticker_id, orderId=orderid)

    def parse_order_update(self, result):
        symbol = None
        orig_id = None
        order_id = None
        side = None
        order_type = None
        order_price = 0
        stop_price = 0
        order_size = 0
        order_status = None
        exec_type = None
        reject_reason = None
        ts = 0

        if self.simulate:
            return None

        # maybe use for debug
        #self.logger.info("parse_order_update={}".format(result))

        if 'c' in result: order_id = result['c']
        if 'C' in result: orig_id = result['C']
        if 'r' in result: reject_reason = result['r']
        if 's' in result: symbol = result['s']
        if 'S' in result: side = result['S']
        if 'o' in result: order_type = result['o']
        if 'q' in result: order_size = result['q']
        if 'p' in result: order_price = result['p']
        if 'P' in result: stop_price = result['P']
        if 'X' in result: order_status = result['X']
        if 'x' in result: exec_type = result['x']
        if 'T' in result: ts = result['T']

        if not symbol:
            return None

        msg_status = TraderMessage.MSG_NONE

        if not order_type:
            return None

        msg_type = Order.get_order_msg_type(order_type)

        if exec_type == 'TRADE' and order_status == 'FILLED':
            if side == 'BUY':
                msg_status = TraderMessage.MSG_BUY_COMPLETE
            elif side == 'SELL':
                msg_status = TraderMessage.MSG_SELL_COMPLETE
        elif exec_type == 'REJECTED' and order_status == 'REJECTED':
            if side == 'BUY':
                msg_status = TraderMessage.MSG_BUY_FAILED
            elif side == 'SELL':
                msg_status = TraderMessage.MSG_SELL_FAILED

        order_update = OrderUpdate(symbol, order_price, stop_price, order_size, order_type, exec_type,
                                   side, ts, order_id, orig_id, order_status, reject_reason, msg_type, msg_status)

        return order_update


    # parse json response to binance API order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        orderid = None
        origqty = 0
        quoteqty = 0
        side = None
        commission = 0
        status = None
        prices = []
        type = None
        order_type = None
        symbol = symbol

        if self.simulate:
            return None

        # maybe use for debug
        #self.logger.info("parse_order_result={}".format(result))

        if 'orderId' in result: orderid = result['orderId']
        if 'origQty' in result: origqty = result['origQty']
        fills = result['fills']
        if 'cummulativeQuoteQty' in result: quoteqty = float(result['cummulativeQuoteQty'])
        if 'symbol' in result: symbol = result['symbol']
        if 'status' in result: status = result['status']
        if 'type' in result: order_type = result['type']
        if 'side' in result: side = result['side']
        if 'price' in result and float(result['price']) != 0:
            prices.append(float(result['price']))

        for fill in fills:
            if 'side' in fill: side = fill['side']
            if 'type' in fill: order_type = fill['type']
            if 'status' in fill: status = fill['status']
            if 'price' in fill and float(fill['price']) != 0:
                prices.append(float(result['price']))
            if 'type' in fill: order_type = fill['type']
            if 'symbol' in fill: symbol = fill['symbol']
            if 'commission' in fill: commission = fill['commission']

        if not symbol or (status != 'FILLED' and status != 'CANCELED'):
            return None

        if not side or not order_type:
            return None

        price = 0
        if len(prices) != 0:
            if side == 'BUY':
                price = max(prices)
            elif side == 'SELL':
                price = min(prices)

        side_type = Order.SIDE_UNKNOWN
        if side == 'BUY':
            side_type = Order.SIDE_BUY
        elif side == 'SELL':
            side_type = Order.SIDE_SELL

        if status == 'FILLED':
            type = TraderMessage.get_order_msg_cmd(order_type, side)
        elif status == 'CANCELED' and side == 'BUY':
            type = TraderMessage.MSG_BUY_CANCEL
        elif status == 'CANCELED' and side == 'SELL':
            type = TraderMessage.MSG_SELL_CANCEL
        elif status == 'REJECTED' and side == 'BUY':
            type = TraderMessage.MSG_BUY_FAILED
        elif status == 'REJECTED' and side == 'SELL':
            type = TraderMessage.MSG_SELL_FAILED

        order = Order(symbol=symbol,
                      price=price,
                      size=origqty,
                      type=type,
                      side=side_type,
                      orderid=orderid,
                      quote_size=quoteqty,
                      commission=commission,
                      sig_id=sigid)

        # maybe use for debug
        #self.logger.info("order: {}".format(str(order)))
        return order
