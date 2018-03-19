#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from trader.myhelpers import *
from trader.TradeRange import TradeRange

if __name__ == '__main__':
    ticker = 'ETH-BTC'
    trade_range = TradeRange(ticker_id=ticker)
    prices = trade_range.get_prices_4hr() #trade_range.get_prices_24hr()

    #price_crossovers, crossover_counts = trade_range.calc_range_from_prices(prices)
    price_crossovers = trade_range.get_price_crossover_counts(prices)

    print(prices)
    print(price_crossovers)

    total_count = 0
    for value in price_crossovers.values():
        total_count += value

    print(total_count)

    middle_count = (max(price_crossovers.values()) + min(price_crossovers.values())) / 2
    print(middle_count)

    #print(crossover_counts)

    for price, count in price_crossovers.items():
        if count > middle_count / 2:
            color = '#{0:06x}'.format(int('0xffffbf', 16) - count ** 3) #int(hex(count), 16))
            #print(count, color)
            plt.axhline(y=price, c=color)

    #for count, prices in crossover_counts.items():
    #    print(prices)
    #    color = '#{0:06x}'.format(int('0xffffbf', 16) - count ** 4)  # int(hex(count), 16))
    #    if count > 10:
    #        plt.axhspan(min(prices), max(prices), alpha=0.5, color=color)

    #print(crossover_counts)
    #print(trade_range.get_indices_by_price(prices))
    #print(trade_range.get_largest_indices_by_price(prices))
    plt.plot(prices)
    #plt.axhline(y=1)
    plt.show()
