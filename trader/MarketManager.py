# manage streaming market data, and deliver at uniform rate to strategy
from trader.indicator.test.DTWMA import DTWMA


class MarketManager(object):
    def __init__(self):
        self.market_items = {}
        self.prev_timestamp = 0
        self.timestamp = 0

    def reset(self):
        self.prev_timestamp = self.timestamp
        for item in self.market_items.values():
            item.reset()

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
        self.dtwma = DTWMA(window=30)
        self.result = 0
        self.kline = None

    def reset(self):
        self.kline = None

    def update(self, kline):
        if not self.kline:
            self.kline = kline
            self.kline.high = self.kline.close
            self.kline.low = self.kline.close
            return

        if kline.close < self.kline.low:
            self.kline.low = kline.close
        if kline.close > self.kline.high:
            self.kline.high = kline.close

        self.dtwma.update(kline.close, kline.ts)
        self.kline.close = self.dtwma.result
        self.kline.volume += kline.volume
        self.kline.ts = kline.ts

    def get_kline(self):
        return self.kline
