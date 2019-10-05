# Market data frame
# Frame is used to represent market financial data


class Frame(object):
    TYPE_WS_FRAME = 1
    TYPE_RT_KLINE_FRAME = 2
    TYPE_DB_KLINE_FRAME = 3

    def __init__(self, frame_type, kline=None):
        self.frame_type = frame_type
        self.kline = kline
