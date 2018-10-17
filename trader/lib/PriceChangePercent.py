class PriceChangePercent(object):
    def __init__(self, time_period=300):
        self.time_period = time_period
        self.klines = []
        self.result = 0

    def update(self, close, ts):
        self.klines.append(KlineSmall(close, ts))

        if (ts - self.klines[0].ts) < self.time_period * 1000:
            return self.result

        for kline in self.klines:
            if (ts - kline.ts) > self.time_period * 1000:
                self.klines.remove(kline)
            else:
                break

        self.result = 100.0 * (close - self.klines[0].close) / self.klines[0].close

class KlineSmall(object):
    def __init__(self, close, ts):
        self.close = close
        self.ts = ts
