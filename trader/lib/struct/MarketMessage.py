# Market Data Message
# Data packet is used to represent single market financial data message
from .Kline import Kline

class MarketMessage(object):
    TYPE_EMPTY_MSG = 0
    TYPE_WS_MSG = 1
    TYPE_RT_KLINE_MSG = 2
    TYPE_DB_KLINE_MSG = 3

    def __init__(self, symbol, msg_type, data=None, kline=None):
        self.msg_type = msg_type
        self.symbol = symbol

        if msg_type == MarketMessage.TYPE_EMPTY_MSG:
            return

        if data and self.msg_type == MarketMessage.TYPE_WS_MSG:
            self.ts = int(data.get('ts', 0))
            self.ask = float(data.get('ask', 0))
            self.bid = float(data.get('bid', 0))
            self.price = float(data.get('price', 0))
            self.size = float(data.get('size', 0))
        elif not kline:
            if msg_type == MarketMessage.TYPE_RT_KLINE_MSG or msg_type == MarketMessage.TYPE_DB_KLINE_MSG:
                self.kline = Kline()
                self.kline.symbol = symbol
                self.kline.ts = int(data.get('ts', 0))
                self.kline.open = float(data.get('open', 0))
                self.kline.close = float(data.get('close', 0))
                self.kline.low = float(data.get('low', 0))
                self.kline.high = float(data.get('high', 0))
                self.kline.volume = float(data.get('volume', 0))
        else:
            self.kline = kline
            if not self.kline.symbol:
                self.kline.symbol = symbol

    # Update MarketMessage without needing to re-create a new instance of object
    def update(self, data=None, kline=None):
        if self.msg_type == MarketMessage.TYPE_EMPTY_MSG:
            return

        if data and self.msg_type == MarketMessage.TYPE_WS_MSG:
            self.ts = int(data.get('ts', 0))
            self.ask = float(data.get('ask', 0))
            self.bid = float(data.get('bid', 0))
            self.price = float(data.get('price', 0))
            self.size = float(data.get('size', 0))
        elif data and self.kline:
            if self.msg_type == MarketMessage.TYPE_RT_KLINE_MSG or self.msg_type == MarketMessage.TYPE_DB_KLINE_MSG:
                self.kline.ts = int(data.get('ts', 0))
                self.kline.open = float(data.get('open', 0))
                self.kline.close = float(data.get('close', 0))
                self.kline.low = float(data.get('low', 0))
                self.kline.high = float(data.get('high', 0))
                self.kline.volume = float(data.get('volume', 0))
        elif kline:
            if not kline.symbol and self.kline:
                kline.symbol = self.kline.symbol
            self.kline = kline
