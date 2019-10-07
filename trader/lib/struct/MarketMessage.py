# Market Data Message
# Data packet is used to represent single market financial data message


class MarketMessage(object):
    TYPE_WS_MSG = 1
    TYPE_RT_KLINE_MSG = 2
    TYPE_DB_KLINE_MSG = 3

    def __init__(self, frame_type, data=None, kline=None):
        self.frame_type = frame_type
        self.kline = kline
