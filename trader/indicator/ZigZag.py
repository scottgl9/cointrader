# ZigZag indicator / price filter
# cutoff is percent change required to consider as zigzag


class ZigZag:
    def __init__(self, window=12, zigzag_window=30, cutoff=0.05):
        self.window = window
        self.zigzag_window = zigzag_window
        self.cutoff = cutoff
        self.prices = []
        self.zigzags = []
        self.last_price = 0.0
        self.last_zigzag = 0.0
        self.prev_last_zigzag = 0.0
        self.result = 0.0
        self.age = 0
        self.age_zigzag = 0.0
        self.counter = 0
        self.counter_last_zigzag = 0

    # Zigzag must be either:
    # 1) price1 < price2 and price2 > price3
    # 2) price1 > price2 and price2 < price3
    # non zigzag if price1 < price2 < price3 or
    # price1 > price2 > price3
    def update_remove_nonzigzag(self, current):
        if self.prev_last_zigzag < self.last_zigzag < current:
            #self.age_zigzag = (int(self.age_zigzag) - 1) % self.zigzag_window
            #self.zigzags[int(self.age_zigzag)] = current
            self.last_zigzag = self.prev_last_zigzag
        elif self.prev_last_zigzag > self.last_zigzag > current:
            #self.age_zigzag = (int(self.age_zigzag) - 1) % self.zigzag_window
            #self.zigzags[int(self.age_zigzag)] = current
            self.last_zigzag = self.prev_last_zigzag

    def update_from_kline(self, price, low, high):
        if abs(price - low) > abs(price - high):
            return self.update(high)
        elif abs(price - low) < abs(price - high):
            return self.update(low)
        return self.update(price)

    def update(self, price):
        if float(price) == self.last_price:
            self.result = 0.0
            return self.result

        if len(self.prices) < self.window:
            self.prices.append(float(price))
        else:
            self.prices[int(self.age)] = float(price)

        if self.last_price != 0.0:
            change = abs(float(price) - self.last_price) / self.last_price
            change_zigzag = self.cutoff/100.0
            if self.last_zigzag != 0.0:
                change_zigzag = abs(float(price) - self.last_zigzag) / self.last_zigzag
            if change >= self.cutoff / 100.0 and change_zigzag >= self.cutoff/100.0 and \
               self.counter > self.counter_last_zigzag + 6:
                if len(self.zigzags) > 3:
                    self.update_remove_nonzigzag(float(price))

                if self.prev_last_zigzag == self.last_zigzag:
                    self.result = 0.0
                else:
                    self.result = self.prev_last_zigzag
                self.prev_last_zigzag = self.last_zigzag

                if self.result != 0.0 and len(self.zigzags) < self.zigzag_window:
                    self.zigzags.append(float(price))
                elif self.result != 0.0:
                    self.zigzags[int(self.age_zigzag)] = float(price)

                self.age_zigzag = (self.age_zigzag + 1) % self.zigzag_window
                self.counter_last_zigzag = self.counter

                self.last_zigzag = float(price)
            else:
                self.result = 0.0

        self.last_price = price
        self.age = (self.age + 1) % self.window
        self.counter += 1
        return self.result
