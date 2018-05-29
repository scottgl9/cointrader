class Message(object):
    ID_MULTI = 'MULTI'
    MSG_MARKET_SELL_ALL = 1
    MSG_MARKET_BUY = 2
    MSG_MARKET_SELL = 3

    def __init__(self, src_id, dst_id, cmd, price=0.0, size=0.0, buy_price=0.0):
        self.src_id = src_id
        self.dst_id = dst_id
        self.cmd = cmd
        self.price = price
        self.size = size
        self.buy_price = buy_price
