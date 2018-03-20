from trader.indicator.SMA import SMA
from trader.indicator.EMA import EMA

# IDEA: get range with highest level of oscillation

class MeasureTrend(object):
    def __init__(self, window=50):
        self.prices = []
        self.last_price = 0.0
        self.sma_prices = []
        self.window = window
        self.sma = EMA(12)

    def update_price(self, price):
        if self.last_price != 0.0 and price == self.last_price:
            return
        if len(self.prices) > self.window:
            self.prices.pop(0)
            self.sma_prices.pop(0)

        self.prices.append(float(price))
        self.sma_prices.append(self.sma.update(price))
        self.last_price = price

    def peak_detected(self):
        if len(self.sma_prices) < self.window:
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
        if len(self.sma_prices) < self.window:
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
        if len(self.sma_prices) < self.window:
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
        if len(self.sma_prices) < self.window:
            return 0.0
        i = len(self.sma_prices) - 8
        if min(self.sma_prices) >= self.sma_prices[i]:
            return self.sma_prices[i]
        #for i in range(1, len(self.sma_prices) - 1):
        #    if self.sma_prices[i-1] > self.sma_prices[i] and self.sma_prices[i+1] > self.sma_prices[i]:
        #        return self.sma_prices[i]
        return 0.0

    def trending_upward(self):
        if len(self.sma_prices) < self.window:
            return False
        change_down = 0.0
        change_up = 0.0
        count_down = 0
        count_up = 0
        for i in range(0, len(self.sma_prices) - 1):
            if self.sma_prices[i] < self.sma_prices[i + 1]:
                change_up += self.sma_prices[i + 1] - self.sma_prices[i]
                count_up += 1
            elif self.sma_prices[i] > self.sma_prices[i + 1]:
                change_down += self.sma_prices[i] - self.sma_prices[i + 1]
                count_down += 1
        if count_up >= int(0.75 * len(self.sma_prices)):
            return True
        #if change_up >= (10.0 * change_down) and max(self.sma_prices) == self.sma_prices[-1] \
        #    and min(self.sma_prices) == self.sma_prices[0]:
        #    return True
        return False

    def trending_downward(self):
        if len(self.sma_prices) < self.window:
            return False
        change_down = 0.0
        change_up = 0.0
        count_down = 0
        count_up = 0
        for i in range(0, len(self.sma_prices) - 1):
            if self.sma_prices[i] < self.sma_prices[i + 1]:
                change_up += self.sma_prices[i + 1] - self.sma_prices[i]
                count_up += 1
            elif self.sma_prices[i] > self.sma_prices[i + 1]:
                change_down += self.sma_prices[i] - self.sma_prices[i + 1]
                count_down += 1
        #if change_down >= (10.0 * change_up) and max(self.sma_prices) == self.sma_prices[0] \
        #    and min(self.sma_prices) == self.sma_prices[-1]:
        #    return True
        if count_down >= int(0.75 * len(self.sma_prices)):
            return True
        return False

    #def trending_upward(self):
    #    if len(self.sma_prices) < 50:
    #        return False
    #    count = 0
    #    for i in range(0, len(self.sma_prices) - 1):
    #        if self.sma_prices[i] <= self.sma_prices[i+1]:
    #            count += 1
    #    if (0.85 * len(self.sma_prices)) <= float(count):
    #        return True
    #    return False

    #def trending_downward(self):
    #    if len(self.sma_prices) < 50:
    #        return False
    #    count = 0
    #    for i in range(0, len(self.sma_prices) - 1):
    #        if self.sma_prices[i] >= self.sma_prices[i+1]:
    #            count += 1
    #    if (0.85 * len(self.sma_prices)) <= float(count):
    #        return True
    #    return False
