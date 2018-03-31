from trader.indicator.EMA import EMA


class PPO:
    def __init__(self, short_weight=12.0, long_weight=26.0, signal_weight=9.0):
        self.last_result = 0.0
        self.result = 0.0
        self.shortEMA = 0.0
        self.longEMA = 0.0
        self.diff = 0.0
        self.ppo = 0.0
        self.short_weight = short_weight
        self.long_weight = long_weight
        self.signal_weight = signal_weight
        self.short = EMA(self.short_weight)
        self.long = EMA(self.long_weight)
        self.macd_signal = EMA(self.signal_weight)
        self.ppo_signal = EMA(self.signal_weight)

    def update(self, price):
        self.short.update(price)
        self.long.update(price)
        self.calculatePPO()
        self.macd_signal.update(self.diff)
        self.ppo_signal.update(self.ppo)
        self.result = self.ppo - self.ppo_signal.result

    def calculatePPO(self):
        self.shortEMA = self.short.result
        self.longEMA = self.long.result
        self.diff = self.shortEMA - self.longEMA
        self.ppo = 100.0 * (self.diff / self.longEMA)
