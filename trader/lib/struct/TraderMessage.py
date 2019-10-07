from .Order import Order


class TraderMessage(object):
    ID_ROOT = "ROOT"
    ID_MULTI = 'MULTI'
    MSG_MARKET_SELL_ALL = 1
    MSG_MARKET_BUY = 2
    MSG_MARKET_SELL = 3
    MSG_LIMIT_BUY = 4
    MSG_LIMIT_SELL = 5
    MSG_STOP_LOSS_BUY = 6
    MSG_STOP_LOSS_SELL = 7
    MSG_PROFIT_LIMIT_BUY = 32
    MSG_PROFIT_LIMIT_SELL = 33
    MSG_STOP_LOSS_LIMIT_BUY = 34
    MSG_STOP_LOSS_LIMIT_SELL = 35
    MSG_TAKE_PROFIT_BUY = 36
    MSG_TAKE_PROFIT_SELL = 37
    MSG_BUY_COMPLETE = 8
    MSG_SELL_COMPLETE = 9
    MSG_BUY_REPLACE = 10
    MSG_SELL_REPLACE = 11
    MSG_BUY_FAILED = 12
    MSG_SELL_FAILED = 13
    MSG_BUY_UPDATE = 14
    MSG_SELL_UPDATE = 15
    MSG_BUY_CANCEL = 16
    MSG_SELL_CANCEL = 17
    MSG_BUY_DISABLE = 18
    MSG_SELL_DISABLE = 19
    MSG_BUY_ENABLE = 20
    MSG_SELL_ENABLE = 21
    MSG_ORDER_SIZE_UPDATE = 22
    MSG_NONE = 23
    # TYPE_MARKET = 24
    # TYPE_LIMIT = 25
    # TYPE_STOP_LOSS = 26
    # TYPE_STOP_LOSS_LIMIT = 27
    # TYPE_PROFIT_LIMIT = 28
    # TYPE_TAKE_PROFIT = 29
    # TYPE_LIMIT_MAKER = 30
    # TYPE_NONE = 31

    def __init__(self, src_id, dst_id, cmd, sig_id=0, price=0.0, size=0.0, buy_price=0.0, ts=0,
                 asset_info=None, order_type=Order.TYPE_MARKET, buy_type=0, sell_type=0, sig_oid=0):
        self.src_id = src_id
        self.dst_id = dst_id
        self.cmd = cmd
        self.sig_id = sig_id
        # for strategy which allows multiple orders per signal, set sig_oid (signal order id)
        self.sig_oid = sig_oid
        self.price = price
        self.size = size
        self.buy_price = buy_price
        self.ts = ts
        # AssetInfo class object stored in self.asset_info
        self.asset_info = asset_info
        self.order_type = order_type
        self.buy_type = buy_type
        self.sell_type = sell_type
        self.read = False

    def mark_read(self):
        self.read = True

    def is_read(self):
        return self.read

    @staticmethod
    def get_type_from_cmd(cmd):
        if cmd == TraderMessage.MSG_MARKET_BUY:
            msg_type = Order.TYPE_MARKET
        elif cmd == TraderMessage.MSG_MARKET_SELL:
            msg_type = Order.TYPE_MARKET
        elif cmd == TraderMessage.MSG_LIMIT_BUY:
            msg_type = Order.TYPE_LIMIT
        elif cmd == TraderMessage.MSG_LIMIT_SELL:
            msg_type = Order.TYPE_LIMIT
        elif cmd == TraderMessage.MSG_STOP_LOSS_BUY:
            msg_type = Order.TYPE_STOP_LOSS
        elif cmd == TraderMessage.MSG_STOP_LOSS_SELL:
            msg_type = Order.TYPE_STOP_LOSS
        elif cmd == TraderMessage.MSG_STOP_LOSS_LIMIT_BUY:
            msg_type = Order.TYPE_STOP_LOSS_LIMIT
        elif cmd == TraderMessage.MSG_STOP_LOSS_LIMIT_SELL:
            msg_type = Order.TYPE_STOP_LOSS_LIMIT
        elif cmd == TraderMessage.MSG_PROFIT_LIMIT_BUY:
            msg_type = Order.TYPE_PROFIT_LIMIT
        elif cmd == TraderMessage.MSG_PROFIT_LIMIT_SELL:
            msg_type = Order.TYPE_PROFIT_LIMIT
        elif cmd == TraderMessage.MSG_TAKE_PROFIT_BUY:
            msg_type = Order.TYPE_TAKE_PROFIT
        elif cmd == TraderMessage.MSG_TAKE_PROFIT_SELL:
            msg_type = Order.TYPE_TAKE_PROFIT
        else:
            msg_type = Order.TYPE_NONE

        return msg_type

    @staticmethod
    def get_msg_cmd_string(cmd):
        if cmd == TraderMessage.MSG_MARKET_SELL_ALL: return 'MARKET_SELL_ALL'
        elif cmd == TraderMessage.MSG_MARKET_BUY: return 'MARKET_BUY'
        elif cmd == TraderMessage.MSG_MARKET_SELL: return 'MARKET_SELL'
        elif cmd == TraderMessage.MSG_LIMIT_BUY: return 'LIMIT_BUY'
        elif cmd == TraderMessage.MSG_LIMIT_SELL: return 'LIMIT_SELL'
        elif cmd == TraderMessage.MSG_STOP_LOSS_BUY: return 'STOP_LOSS_BUY'
        elif cmd == TraderMessage.MSG_STOP_LOSS_SELL: return 'STOP_LOSS_SELL'
        elif cmd == TraderMessage.MSG_PROFIT_LIMIT_BUY: return 'PROFIT_LIMIT_BUY'
        elif cmd == TraderMessage.MSG_PROFIT_LIMIT_SELL: return 'PROFIT_LIMIT_SELL'
        elif cmd == TraderMessage.MSG_STOP_LOSS_LIMIT_BUY: return 'STOP_LOSS_LIMIT_BUY'
        elif cmd == TraderMessage.MSG_STOP_LOSS_LIMIT_SELL: return 'STOP_LOSS_LIMIT_SELL'
        elif cmd == TraderMessage.MSG_TAKE_PROFIT_BUY: return 'TAKE_PROFIT_BUY'
        elif cmd == TraderMessage.MSG_TAKE_PROFIT_SELL: return 'TAKE_PROFIT_SELL'
        elif cmd == TraderMessage.MSG_BUY_COMPLETE: return 'BUY_COMPLETE'
        elif cmd == TraderMessage.MSG_SELL_COMPLETE: return 'SELL_COMPLETE'
        elif cmd == TraderMessage.MSG_BUY_REPLACE: return 'BUY_REPLACE'
        elif cmd == TraderMessage.MSG_SELL_REPLACE: return 'SELL_REPLACE'
        elif cmd == TraderMessage.MSG_BUY_FAILED: return 'BUY_FAILED'
        elif cmd == TraderMessage.MSG_SELL_FAILED: return 'SELL_FAILED'
        elif cmd == TraderMessage.MSG_BUY_UPDATE: return 'BUY_UPDATE'
        elif cmd == TraderMessage.MSG_SELL_UPDATE: return 'SELL_UPDATE'
        elif cmd == TraderMessage.MSG_BUY_CANCEL: return 'BUY_CANCEL'
        elif cmd == TraderMessage.MSG_SELL_CANCEL: return 'SELL_CANCEL'
        elif cmd == TraderMessage.MSG_BUY_DISABLE: return 'BUY_DISABLE'
        elif cmd == TraderMessage.MSG_SELL_DISABLE: return 'SELL_DISABLE'
        elif cmd == TraderMessage.MSG_BUY_ENABLE: return 'BUY_ENABLE'
        elif cmd == TraderMessage.MSG_SELL_ENABLE: return 'SELL_ENABLE'
        elif cmd == TraderMessage.MSG_ORDER_SIZE_UPDATE: return 'ORDER_SIZE_UPDATE'
        elif cmd == TraderMessage.MSG_NONE: return 'NONE'
        return None

    @staticmethod
    def get_msg_type_string(msg_type):
        if msg_type == Order.TYPE_MARKET: return 'MARKET'
        elif msg_type == Order.TYPE_LIMIT: return 'LIMIT'
        elif msg_type == Order.TYPE_STOP_LOSS: return 'STOP_LOSS'
        elif msg_type == Order.TYPE_STOP_LOSS_LIMIT: return 'STOP_LOSS_LIMIT'
        elif msg_type == Order.TYPE_PROFIT_LIMIT: return 'TAKE_PROFIT_LIMIT'
        elif msg_type == Order.TYPE_TAKE_PROFIT: return 'TAKE_PROFIT'
        elif msg_type == Order.TYPE_LIMIT_MAKER: return 'LIMIT_MAKER'
        elif msg_type == Order.TYPE_NONE: return 'NONE'
        return None

    @staticmethod
    def get_order_msg_cmd(order_type, side):
        if order_type == 'MARKET' and side == 'BUY':
            type = TraderMessage.MSG_MARKET_BUY
        elif order_type == 'MARKET' and side == 'SELL':
            type = TraderMessage.MSG_MARKET_SELL
        elif order_type == 'LIMIT' and side == 'BUY':
            type = TraderMessage.MSG_LIMIT_BUY
        elif order_type == 'LIMIT' and side == 'SELL':
            type = TraderMessage.MSG_LIMIT_SELL
        elif order_type == "STOP_LOSS" and side == 'BUY':
            type = TraderMessage.MSG_STOP_LOSS_BUY
        elif order_type == "STOP_LOSS" and side == 'SELL':
            type = TraderMessage.MSG_STOP_LOSS_SELL
        elif order_type == "STOP_LOSS_LIMIT" and side == "BUY":
            type = TraderMessage.MSG_STOP_LOSS_LIMIT_BUY
        elif order_type == "STOP_LOSS_LIMIT" and side == "SELL":
            type = TraderMessage.MSG_STOP_LOSS_LIMIT_SELL
        elif order_type == "TAKE_PROFIT_LIMIT" and side == "BUY":
            type = TraderMessage.MSG_PROFIT_LIMIT_BUY
        elif order_type == "TAKE_PROFIT_LIMIT" and side == "SELL":
            type = TraderMessage.MSG_PROFIT_LIMIT_SELL
        elif order_type == "TAKE_PROFIT" and side == "BUY":
            type = TraderMessage.MSG_TAKE_PROFIT_BUY
        elif order_type == "TAKE_PROFIT" and side == "SELL":
            type = TraderMessage.MSG_TAKE_PROFIT_SELL
        else:
            type = TraderMessage.MSG_NONE
        return type
