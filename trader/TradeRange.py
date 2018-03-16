# This strategy is ideal for a sideways market with a large price swing
# The idea of the algorithm is to find the range with the largest number of
# price crossovers through the range. One way to do this is to use EMA which
# should always be in the center of the trading range, and an EMA which closely
# follows the price
from trader.indicator.EMA import EMA
from trader.myhelpers import *

# kline format: [ time, low, high, open, close, volume ]

class TradeRange(object):
    def __init__(self, accnt=None, ticker_id=None):
        self.peaks = []
        self.valleys = []
        self.ema_prices= []
        self.ema = EMA(8)
        self.major_resistance = 0.0
        self.major_support = 0.0
        self.active_resistance = 0.0
        self.active_support = 0.0
        self.accnt = accnt
        self.ticker_id = ticker_id

    def update(self, price):
        self.ema_prices.append(self.ema.update(price))

    def get_prices_24hr(self):
        prices = []
        for kline in retrieve_klines_days(self.ticker_id, days=1):
            prices.append(float(kline[3]))
            prices.append(float(kline[4]))

        return prices

    def get_prices_4hr(self):
        prices= []

        for kline in retrieve_klines_last_hour(self.ticker_id, hours=4):
            prices.append(float(kline[3]))
            prices.append(float(kline[4]))

        return prices

    # create dictionary where price_crossovers[price] = cross count
    def get_price_crossover_counts(self, prices):
        if self.ticker_id.endswith('USD'):
            step_size = 0.01
        else:
            step_size = 0.00001

        round_size = '{:f}'.format(step_size).index('1') - 1
        print(round_size)
        current_price = round(min(prices), round_size)
        price_crossovers = {}
        prices_completed = []

        counter = 0.0

        max_prices = round(max(prices), round_size)

        while current_price <= max_prices:
            cross_count = 0
            counter += 1.0

            #print(int(100.0 * current_price / max_prices), current_price)

            if current_price in prices_completed:#current_price not in prices or current_price in prices_completed:
                current_price = round(current_price + step_size, round_size)
                continue

            for i in range(0, len(prices) - 1):
                #if prices[i] == prices[i+1]: continue
                if prices[i] <= current_price <= prices[i+1]          \
                        or prices[i] >= current_price >= prices[i+1]  \
                        or prices[i] == current_price:
                    cross_count += 1

            price_crossovers[current_price] = cross_count
            prices_completed.append(current_price)
            current_price = round(current_price + step_size, round_size)

        return price_crossovers

    # create dictionary where crossover_counts[cross_count] = list of prices with same cross_count
    def calc_range_from_prices(self, prices):
        self.major_resistance = max(prices)
        self.major_support = min(prices)
        print(self.major_support, self.major_resistance)

        price_crossovers = self.get_price_crossover_counts(prices)

        crossover_counts = {}
        for key, value in price_crossovers.items():
            #if value <= 10: continue
            price_list = [k for (k, v) in price_crossovers.iteritems() if v == value]
            #for ksub, vsub in price_crossovers.items():
            #    if vsub == v: price_list.append(ksub)
            range_size = round(max(price_list) - min(price_list), 2)
            crossover_counts[value] = sorted(price_list) #, round(range_size, 2)]

        return price_crossovers, crossover_counts

    # return dictionary for which each price (key) is a list of all
    # indices (value) in prices that have that price value
    def get_indices_by_price(self, prices):
        if self.ticker_id.endswith('USD'):
            step_size = 0.01
        else:
            step_size = 0.00001

        round_size = '{:f}'.format(step_size).index('1') - 1
        print(round_size)
        current_price = self.major_support
        price_indices = {}

        while current_price <= self.major_resistance:
            indices = []
            for i in range(0, len(prices) - 1):
                if prices[i] == current_price:
                    indices.append(i)
            if len(indices) > 2:
                price_indices[current_price] = indices
            current_price = round(current_price + step_size, round_size)
        return price_indices

    def get_largest_indices_by_price(self, prices):
        indices = self.get_indices_by_price(prices)
        max_indices = []
        result = {}
        price_index = 0.0
        for k,v in indices.items():
            if len(v) > len(max_indices):
                max_indices = v
                price_index = k

        result[price_index] = max_indices

        return result

    def get_active_range(self, prices):
        result = []
        price_crossovers, crossover_counts = self.calc_range_from_prices(prices)
        cutoff = (min(price_crossovers.values()) + max(price_crossovers.values())) / 2.0
        for count, cross_price in crossover_counts.items():
            if count < cutoff or len(cross_price) < 2: continue
            result.append((count, cross_price))
        return result
