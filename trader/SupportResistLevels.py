from trader.indicator.EMA import  EMA

class SupportResistLevels(object):
    def __init__(self, window=30):
        self.window = window
        self.ema_low = EMA(26)
        self.ema_high = EMA(26)
        self.kline_prices = []
        self.kline_lows = []
        self.kline_highs = []
        self.low = 0.0
        self.high = 0.0
        self.prev_low = 0.0
        self.prev_high = 0.0
        self.last_prev_low = 0.0
        self.last_prev_high = 0.0
        self.age = 0

    def update(self, close, low, high):
        if len(self.kline_prices) < self.window:
            self.kline_prices.append(float(close))
            self.kline_lows.append(float(low))
            self.kline_highs.append(float(high))
        else:
            self.kline_prices[int(self.age)] = float(close)
            self.kline_lows[int(self.age)] = float(low)
            self.kline_highs[int(self.age)] = float(high)
            if self.age == 0:
                self.last_prev_low = self.prev_low
                self.last_prev_high = self.prev_high
                self.prev_low = self.low
                self.prev_high = self.high
                self.low = self.ema_high.update(min(self.kline_lows))
                self.high = self.ema_low.update(max(self.kline_highs))

        self.age = (self.age + 1) % self.window

        if self.last_prev_low == 0 or self.prev_low == 0:
            return 0, 0
        result_low = self.prev_low #(self.last_prev_low + self.prev_low) / 2.0
        result_high = self.prev_high # (self.last_prev_high + self.prev_high) / 2.0

        return result_low, result_high
