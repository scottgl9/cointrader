from trader.indicator.SMA import SMA


# IDEA: get range with highest level of oscillation

class MeasureTrend(object):
    def __init__(self):
        self.prices = []
        self.last_price = 0.0
        self.sma_prices = []
        self.sma = SMA(8)

    def update_price(self, price):
        if self.last_price != 0.0 and price == self.last_price:
            return
        if len(self.prices) > 50:
            self.prices.pop(0)
            self.sma_prices.pop(0)

        self.prices.append(float(price))
        self.sma_prices.append(self.sma.update(price))

    def peak_detected(self):
        if len(self.sma_prices) < 50:
            return False

        detected = False
        #for i in range(1, len(self.sma_prices) - 1):
        i = len(self.sma_prices) - 4
        if self.sma_prices[i-1] < self.sma_prices[i] and self.sma_prices[i+1] < self.sma_prices[i]:
            detected = True
            #for j in range(2, 32):
            #    if (i-j) < 0 or (i+j) > len(self.sma_prices) - 1:
            #        break
            #    if self.sma_prices[i-j] > self.sma_prices[i] or self.sma_prices[i+j] > self.sma_prices[i]:
            #        detected = False
            #        break
        return detected

    def valley_detected(self):
        if len(self.sma_prices) < 50:
            return False

        detected = False
        for i in range(1, len(self.sma_prices) - 1):
            if self.sma_prices[i-1] > self.sma_prices[i] and self.sma_prices[i+1] > self.sma_prices[i]:
                detected = True
                for j in range(2, 32):
                    if (i-j) < 0 or (i+j) > len(self.sma_prices) - 1:
                        break
                    if self.sma_prices[i-j] < self.sma_prices[i] or self.sma_prices[i+j] < self.sma_prices[i]:
                        detected = False
                        break
        return detected

    def get_peak_price(self):
        if len(self.sma_prices) < 50:
            return 0.0

        #for i in range(1, len(self.sma_prices) - 1):
        i = len(self.sma_prices) - 8
        if max(self.sma_prices) <= self.sma_prices[i]:
            return self.sma_prices[i]
            #for j in range(2, 32):
            #    if (i-j) < 0 or (i+j) > len(self.sma_prices) - 1:
            #        break
            #    if self.sma_prices[i-j] > self.sma_prices[i] or self.sma_prices[i+j] > self.sma_prices[i]:
            #        detected = False
            #        break
        return 0.0

    def get_valley_price(self):
        if len(self.sma_prices) < 50:
            return 0.0
        i = len(self.sma_prices) - 8
        if min(self.sma_prices) >= self.sma_prices[i]:
            return self.sma_prices[i]
        #for i in range(1, len(self.sma_prices) - 1):
        #    if self.sma_prices[i-1] > self.sma_prices[i] and self.sma_prices[i+1] > self.sma_prices[i]:
        #        return self.sma_prices[i]
        return 0.0

    def trending_upward(self):
        if len(self.sma_prices) < 50:
            return False
        count = 0
        for i in range(0, len(self.sma_prices) - 1):
            if self.sma_prices[i] <= self.sma_prices[i+1]:
                count += 1
        if (0.85 * len(self.sma_prices)) <= float(count):
            return True
        return False

    def trending_downward(self):
        if len(self.sma_prices) < 50:
            return False
        count = 0
        for i in range(0, len(self.sma_prices) - 1):
            if self.sma_prices[i] >= self.sma_prices[i+1]:
                count += 1
        if (0.85 * len(self.sma_prices)) <= float(count):
            return True
        return False
