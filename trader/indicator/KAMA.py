from trader.indicator.EMA import EMA, SMA
import math

# ER = Change/Volatility
# Change = ABS(Close - Close (10 periods ago))
# Volatility = Sum10(ABS(Close - Prior Close))
# Volatility is the sum of the absolute value of the last ten price changes (Close - Prior Close).

# Kaufman's Adaptive Moving Average (KAMA)
class KAMA(object):
    def __init__(self, er_window=10, fast_ema_window=2, slow_ema_window=30):
        self.last_result = 0.0
        self.age = 0
        self.sum = 0.0
        self.er_window = er_window
        self.fast_ema_window = fast_ema_window
        self.slow_ema_window = slow_ema_window

        self.fast_ema = EMA(self.fast_ema_window)
        self.slow_ema = EMA(self.slow_ema_window)
        self.price_sma = SMA(self.er_window)
        self.prices = []
        self.count = 0
        self.result = 0

    def update(self, price):
        volatility = 0.0
        change = 0.0
        sma_price = 0.0
        price = float(price)

        if len(self.prices) < self.er_window:
            tail = 0.0
            sma_price = self.price_sma.update(float(price))
            self.prices.append(price)
            change = 0.0
        else:
            price10 = self.prices[int(self.age)]
            change = round(price - price10, 2)
            tail = self.prices[int(self.age)]
            sma_price = self.price_sma.update(float(price))
            self.prices[int(self.age)] = price
            # the price 10 periods ago is the next price in self.prices

        self.sum += sma_price - tail
        if len(self.prices) != 0:
            volatility = self.sum / float(len(self.prices))

        if volatility == 0.0 or change == 0.0:
            er = 0.0
        else:
            er = round(change / volatility, 2)

        fast_sc = self.fast_ema.update(price)
        slow_sc = self.slow_ema.update(price)

        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2

        # compute KAMA
        self.result = price * sc + self.last_result * (1.0 - sc)
        #self.result = round(self.last_result + sc * (price - self.last_result), 8)

        self.last_result = self.result
        self.count += 1
        self.age = (self.age + 1) % self.er_window

        return self.result
