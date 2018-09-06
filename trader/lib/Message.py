class Message(object):
    ID_MULTI = 'MULTI'
    MSG_MARKET_SELL_ALL = 1
    MSG_MARKET_BUY = 2
    MSG_MARKET_SELL = 3
    MSG_LIMIT_BUY = 4
    MSG_LIMIT_SELL = 5
    MSG_STOP_LOSS_BUY = 6
    MSG_STOP_LOSS_SELL = 7
    MSG_BUY_COMPLETE = 8
    MSG_SELL_COMPLETE = 9
    MSG_BUY_REPLACE = 10
    MSG_SELL_REPLACE = 11
    MSG_BUY_FAILED = 12
    MSG_SELL_FAILED = 13

    def __init__(self, src_id, dst_id, cmd, price=0.0, size=0.0, buy_price=0.0):
        self.src_id = src_id
        self.dst_id = dst_id
        self.cmd = cmd
        self.price = price
        self.size = size
        self.buy_price = buy_price
        self.read = False

    def mark_read(self):
        self.read = True
