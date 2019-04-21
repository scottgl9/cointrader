from .IndicatorBase import IndicatorBase
from trader.lib.ValueLag import ValueLag
# ER = Change/Volatility
# Change = ABS(Close - Close (10 periods ago))
# Volatility = Sum10(ABS(Close - Prior Close))
# Volatility is the sum of the absolute value of the last ten price changes (Close - Prior Close).


# Kaufman's Adaptive Moving Average (KAMA)
class KAMA(IndicatorBase):
    def __init__(self, er_window=10, fast_ema_window=2, slow_ema_window=12, scale=1.0, lagging=False, lag_window=3):
        IndicatorBase.__init__(self, use_close=True)
        self.last_result = 0.0
        self.age = 0
        self.sum = 0.0
        self.er_window = er_window
        self.fast_ema_window = fast_ema_window
        self.slow_ema_window = slow_ema_window
        self.prices = []
        self.result = 0.0
        self.scale = scale
        self.lagging = lagging
        self.value_lag = None
        if self.lagging:
            self.value_lag = ValueLag(window=lag_window)

    def update(self, price, ts=0):
        volatility = 0.0
        price = float(price)

        if self.result == 0.0:
            self.result = price
            return self.result

        if len(self.prices) < self.er_window:
            tail = 0.0
            self.prices.append(price)
            change = 0.0
        else:
            price10 = self.prices[int(self.age)]
            change = price - price10
            tail = self.prices[int(self.age)]
            self.prices[int(self.age)] = price
            # the price 10 periods ago is the next price in self.prices

        self.sum += float(price) - tail
        if len(self.prices) != 0:
            volatility = self.sum / float(len(self.prices))

        if volatility == 0.0 or change == 0.0:
            er = 0.0
        else:
            er = change / volatility

        fast_sc = 2.0 / (self.fast_ema_window * self.scale + 1.0)
        slow_sc = 2.0 / (self.slow_ema_window * self.scale + 1.0)

        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2

        if self.lagging:
            self.last_result = self.value_lag.update(self.result)
        else:
            self.last_result = self.result

        # compute KAMA
        y = self.result
        self.result = price * sc + y * (1.0 - sc)

        self.age = (self.age + 1) % self.er_window

        return self.result
