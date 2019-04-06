class Message(object):
    ID_ROOT = "ROOT"
    ID_MULTI = 'MULTI'
    MSG_MARKET_SELL_ALL = 1
    MSG_MARKET_BUY = 2
    MSG_MARKET_SELL = 3
    MSG_LIMIT_BUY = 4
    MSG_LIMIT_SELL = 5
    MSG_STOP_LOSS_BUY = 6
    MSG_STOP_LOSS_SELL = 7
    MSG_PROFIT_LIMIT_BUY = 31
    MSG_PROFIT_LIMIT_SELL = 32
    MSG_STOP_LOSS_LIMIT_BUY = 33
    MSG_STOP_LOSS_LIMIT_SELL = 34
    MSG_TAKE_PROFIT_BUY = 35
    MSG_TAKE_PROFIT_SELL = 36
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
    TYPE_MARKET = 24
    TYPE_LIMIT = 25
    TYPE_STOP_LOSS = 26
    TYPE_STOP_LOSS_LIMIT = 27
    TYPE_PROFIT_LIMIT = 28
    TYPE_TAKE_PROFIT = 29
    TYPE_NONE = 30

    def __init__(self, src_id, dst_id, cmd, sig_id=0, price=0.0, size=0.0, buy_price=0.0, ts=0,
                 asset_info=None, order_type=TYPE_MARKET, buy_type=0, sell_type=0):
        self.src_id = src_id
        self.dst_id = dst_id
        self.cmd = cmd
        self.sig_id = sig_id
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
