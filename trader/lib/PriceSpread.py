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

    def update(self, price, ts):
        self.sma.update(price)
        if not self.mid_price:
            self.mid_price = price
            return

        if not self.ask_price and price > self.mid_price:
            self.ask_price = price
            return
        elif not self.bid_price and price < self.mid_price:
            self.bid_price = price
            return

        if self.ask_price and not self.bid_price:
            if price > self.ask_price:
                self.last_ask_price = self.ask_price
                self.ask_price = price
                self.last_mid_price = self.mid_price
                self.mid_price = self.last_ask_price
        elif not self.ask_price and self.bid_price:
            if price < self.bid_price:
                self.last_bid_price = self.bid_price
                self.bid_price = price
                self.last_mid_price = self.mid_price
                self.mid_price = self.last_bid_price

        if not self.ask_price or not self.bid_price:
            return

        self.last_spread = self.spread
        self.spread = self.ask_price - self.bid_price

        if price > self.mid_price:
            if price > self.ask_price:
                self.last_ask_price = self.ask_price
                self.ask_price = price
                self.last_mid_price = self.mid_price
                self.mid_price = self.last_ask_price
            elif price < self.ask_price:
                self.last_ask_price = self.ask_price
                self.ask_price = price
        elif price < self.mid_price:
            if price < self.bid_price:
                self.last_bid_price = self.bid_price
                self.bid_price = price
                self.last_mid_price = self.mid_price
                self.mid_price = self.last_bid_price
            elif price > self.bid_price:
                self.last_bid_price = self.bid_price
                self.bid_price = price
        else:
            # price == self.mid_price
            self.bid_price = self.last_bid_price
            self.ask_price = self.last_ask_price
            self.mid_price = self.last_mid_price

        # if float(price) > self.sma.result:
        #     if float(price) != self.last_bid_price and float(price) != self.bid_price:
        #         self.last_ask_price = self.ask_price
        #         self.ask_price = float(price) #self.sma_ask.update((float(price)))
        # elif float(price) < self.sma.result:
        #     if float(price) != self.last_ask_price and float(price) != self.ask_price:
        #         self.last_bid_price = self.bid_price
        #         self.bid_price = float(price) #self.sma_bid.update(float(price))
        #
        return self.bid_price, self.ask_price
