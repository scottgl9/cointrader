from trader.indicator.SMMA import SMMA

class ROC(object):
    def __init__(self, window=30):
        self.window = window
        self.smma = SMMA(14)
        self.price = 0.0
        self.last_price = 0.0
        self.result = 0.0
        self.last_result = 0.0
        self.prev_last_result = 0.0
        self.last_ts = 0
        self.age = 0
        self.rocs = []

    def update(self, price, ts):
        pchange_per_min = 0.0
        self.price = self.smma.update(price)
        if self.last_price != 0.0 and self.price != 0.0:
            pchange = (self.price - self.last_price) / self.last_price
            time_change = (ts - self.last_ts) / 60.0
            if time_change != 0.0:
                pchange_per_min = abs(pchange / time_change)
            if len(self.rocs) < self.window:
                self.rocs.append(pchange_per_min)
            else:
                self.rocs[int(self.age)] = pchange_per_min
            self.result = pchange_per_min
        self.last_price = self.price
        self.last_ts = ts
        self.prev_last_result = self.last_result
        self.last_result = self.result
