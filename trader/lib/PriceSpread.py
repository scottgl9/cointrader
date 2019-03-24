# Break down the moving close price into two classifications: ask or bid
from trader.indicator.SMA import SMA


class PriceSpread(object):
    def __init__(self, window=10):
        self.window = window
        self.sma = SMA(self.window)
        #self.sma_ask = SMA(10)
        #self.sma_bid = SMA(10)
        self.ask_price = 0
        self.bid_price = 0
        self.last_ask_price = 0
        self.last_bid_price = 0
        self.mid_price = 0
        self.last_mid_price = 0
        self.spread = 0
        self.last_spread = 0
        self.last_price = 0

    def update(self, price, ts):
        self.sma.update(price)

        # set mid_price as initial price
        if not self.mid_price:
            self.mid_price = price
            return self.bid_price, self.ask_price

        # determine initial ask_price and bid_price from price
        # in relation to mid_price
        if not self.ask_price and price > self.mid_price:
            self.ask_price = price
            return self.bid_price, self.ask_price
        elif not self.bid_price and price < self.mid_price:
            self.bid_price = price
            return self.bid_price, self.ask_price

        # we have a mid_price and ask_price, need bid_price
        if self.ask_price and not self.bid_price:
            # price > ask_price, so adjust mid_price and ask_price
            if price > self.ask_price:
                self.last_ask_price = self.ask_price
                self.ask_price = price
                self.last_mid_price = self.mid_price
                # update mid_price to last ask price
                self.mid_price = self.last_ask_price
        # we have a mid rice and bid price, need ask_price
        elif not self.ask_price and self.bid_price:
            # price < bid price, so adjust mid_price and bid_price
            if price < self.bid_price:
                self.last_bid_price = self.bid_price
                self.bid_price = price
                # update mid_price to last_bid_price
                self.last_mid_price = self.mid_price
                self.mid_price = self.last_bid_price

        # unable to determine both ask_price and bid_price
        # so wait for next price
        if not self.ask_price or not self.bid_price:
            return self.bid_price, self.ask_price

        if price == self.mid_price:
            self.mid_price = (self.bid_price + self.ask_price) / 2.0

        if self.ask_price == self.last_bid_price:
            self.ask_price = self.last_ask_price
            self.mid_price = self.last_mid_price
        if self.bid_price == self.last_ask_price:
            self.bid_price = self.last_bid_price
            self.mid_price = self.last_mid_price

        # if self.ask_price == self.mid_price:
        #     self.ask_price = self.last_ask_price
        #     self.mid_price = self.last_mid_price
        # if self.bid_price == self.mid_price:
        #     self.bid_price = self.last_bid_price
        #     self.mid_price = self.last_mid_price

        self.last_spread = self.spread
        self.spread = self.ask_price - self.bid_price

        if price > self.mid_price:
            # price > mid_price and price > ask_price
            if price > self.ask_price:
                self.last_ask_price = self.ask_price
                self.ask_price = price
                self.last_mid_price = self.mid_price
                self.mid_price = self.last_ask_price
            # ask_price > price > mid_price
            elif price < self.ask_price:
                self.last_ask_price = self.ask_price
                self.ask_price = price
        elif price < self.mid_price:
            # price < mid_price and price < bid_price
            if price < self.bid_price:
                self.last_bid_price = self.bid_price
                self.bid_price = price
                self.last_mid_price = self.mid_price
                self.mid_price = self.last_bid_price
            # bid_price < price < mid_price
            elif price > self.bid_price:
                self.last_bid_price = self.bid_price
                self.bid_price = price

        return self.bid_price, self.ask_price
