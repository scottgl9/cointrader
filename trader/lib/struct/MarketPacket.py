# Market Data Packet
# Data packet is used to represent single market financial data message/packet


class MarketPacket(object):
    TYPE_WS_PACKET = 1
    TYPE_RT_KLINE_PACKET = 2
    TYPE_DB_KLINE_PACKET = 3

    def __init__(self, frame_type, data=None, kline=None):
        self.frame_type = frame_type
        self.kline = kline
