# manage streaming market data, and deliver at uniform rate to strategy
from trader.indicator.ehler.EMAMA import EMAMA


class MarketManager(object):
    def __init__(self):
        self.market_items = {}
        self.prev_timestamp = 0
        self.timestamp = 0

    def reset(self):
        self.prev_timestamp = self.timestamp

    def ready(self):
        if (self.timestamp - self.prev_timestamp) >= 1000 * 15:
            return True
        return False

    def update(self, symbol, kline):
        if symbol not in self.market_items.keys():
            self.market_items[symbol] = MarketItem(symbol)

        if self.prev_timestamp == 0:
            self.prev_timestamp = kline.ts
        else:
            self.timestamp = kline.ts

        self.market_items[symbol].update(kline)

    def get_klines(self):
        klines = []
        for item in self.market_items.values():
            kline = item.get_kline()
            if kline:
                klines.append(kline)
        return klines


class MarketItem(object):
    def __init__(self, symbol):
        self.symbol = symbol
        self.emama = EMAMA()
        self.result = 0
        self.kline = None

    def update(self, kline):
        self.kline = kline
        #self.emama.update(kline.close)
        #self.result = self.emama.result

    def get_kline(self):
        return self.kline
