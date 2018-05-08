from trader.indicator.SMMA import SMMA

class ROC(object):
    def __init__(self, window=30):
        self.window = window
        #self.smma = SMMA(14)
        self.price = 0.0
        self.last_price = 0.0
        self.result = 0.0
        self.last_result = 0.0
        self.last_ts = 0
        self.age = 0
        self.rocs = []

    def update(self, price, ts):
        pchange_per_min = 0.0
        result = 0
        self.last_price = self.price
        self.price = price
        if self.last_price != 0.0 and self.price != 0.0:
            pchange = (self.price - self.last_price) / self.last_price
            #time_change = (ts - self.last_ts) / 60.0
            #if time_change != 0.0:
            pchange_per_min = abs(pchange) #/ time_change)
            if len(self.rocs) < self.window:
                self.rocs.append(pchange_per_min)
            else:
                self.rocs[int(self.age)] = pchange_per_min
            result = pchange_per_min
        self.last_ts = ts
        self.last_result = self.result
        self.result = result

    def increasing(self):
        return self.last_result != 0 and self.result > self.last_result

    def decreasing(self):
        return self.last_result != 0 and self.result < self.last_result
