#!/usr/bin/env python3

from gdax.myhelpers import *
from gdax.indicator.EMA import EMA
from gdax.indicator.SMMA import SMMA
from gdax.indicator.VWAP import VWAP
from gdax.indicator.MACD import MACD

# kline format: [ time, low, high, open, close, volume ]

def plot_emas_product(plt, product):
    klines = retrieve_klines_last_hour(product, hours=4)
    #klines = retrieve_klines_24hrs(product)
    vwap = VWAP(60)
    #macd = MACD()
    #macd_signal = []
    #for kline in klines:
    #    macd.update(float(kline[3]))
    #    #macd.update()
    #    macd_signal.append(float(macd.signal.result))
    vwap0 = []
    for kline in klines:
        vwap.kline_update(low=kline[1], high=kline[2], close=kline[4], volume=kline[5])
        vwap0.append(vwap.result)
    ema0 = compute_ema_dict_from_klines(klines, 4)
    ema1 = compute_ema_dict_from_klines(klines, 12)
    ema2 = compute_ema_dict_from_klines(klines, 26)
    #compute_ema_crossover_from_klines(ema1, ema2)
    prices = prices_from_kline_data(klines)
    symprice, = plt.plot(prices, label=product)
    sma0 = compute_smma_from_kline_prices(prices, 12)
    sma12, = plt.plot(sma0, label='SMMA12')
    ema4, = plt.plot(ema0["y"], label='EMA4')
    #vwap30, = plt.plot(vwap0, label='VWAP30')
    #macd0, = plt.plot(macd_signal, label='MACDSIG')
    #ema12, = plt.plot(ema1["y"], label='EMA12')
    #ema26, = plt.plot(ema2["y"], label='EMA26')
    #ema50, = plt.plot(compute_ema_from_kline_prices(prices, 50), label='EMA50')
    plt.legend(handles=[symprice, ema4, sma12])
    plt.subplot(212)
    diffs = np.array(sma0) - np.array(ema0["y"][1:])
    ema9 = []
    ema = EMA(12)
    for diff in diffs:
        ema9.append(ema.update(diff))
    plt.plot(ema9)
    diff2 = np.array(diffs) - np.array(ema9)
    plt.plot(diff2)
    #    ema12.append(ema.update(price))
    plt.plot(np.array(sma0) - np.array(ema0["y"][1:]))



def abs_average(values):
    total = 0.0
    for value in values:
        total += abs(value)
    total = total / float(len(values))
    return total

if __name__ == '__main__':
    #mongo_client = MongoClient('mongodb://localhost:27017/')

    #db = mongo_client.cryptocurrency_database
    #LTC_collection = db.LTC_collection

    #data = query_price_last_hour(db)
    #plt.plot(data["y"])
    #plt.plot(compute_ema_last_hour(db, 12)["y"])
    #plt.plot(compute_ema_last_hour(db, 26)["y"])
    #plt.plot(compute_sma_last_day(db)["y"])
    #data2 = compute_ema20_last_hour(db)
    #plt.plot(data2["x"], data2["y"])
    #plt.gcf().autofmt_xdate()
    #myFmt = mdates.DateFormatter('%H:%M')
    #plt.gca().xaxis.set_major_formatter(myFmt)
    #plt.plot(compute_ema20_last_hour(db))
    #plt.show()

    #product='BTC-USD'
    #klines = retrieve_klines_last_hour(product)
    #ema1 = compute_ema_dict_from_klines(klines, 12)
    #ema2 = compute_ema_dict_from_klines(klines, 26)
    #prices = prices_from_kline_data(klines)

    #symprice, = plt.plot(prices, label=product)
    #sma12, = plt.plot(compute_sma_from_kline_prices(prices, 12), label='SMA12')
    #ema12, = plt.plot(ema1["y"], label='EMA12')
    #ema26, = plt.plot(ema2["y"], label='EMA26')
    #ema50, = plt.plot(compute_ema_from_kline_prices(prices, 50), label='EMA50')
    #plt.plot(compute_rsi_from_klines("XRPBTC", "1 day ago UTC"))
    #plt.legend(handles=[symprice, sma12, ema12, ema26, ema50])

    plt.figure(1)
    plt.subplot(211)
    plot_emas_product(plt, 'LTC-USD')
    #plt.figure(2)
    #plt.subplot(212)
    macd = MACD()
    klines = retrieve_klines_24hrs('LTC-USD')
    #klines = retrieve_klines_last_hour('LTC-USD', hours=4)
    macd_data = []
    macd_signal = []
    macd_diff = []
    for kline in klines:
        macd.update(float(kline[3]))
        #macd.update()
        macd_data.append(macd.result)
        macd_signal.append(macd.signal.result)
        macd_diff.append(macd.diff)

    volume_changes = []

    last_price = float(klines[0][4])
    last_volume =float(klines[0][5])

    emavol = EMA(4)
    emaprice = EMA(4)

    for i in range(1, len(klines)):
        #price_changes.append(emaprice.update(float(klines[i][4])))
        volume_changes.append(emavol.update(float(klines[i][5])))
        last_price = float(klines[i][4])
        last_volume = float(klines[i][5])

    avg_volume = abs_average(volume_changes)
    #avg_price = abs_average(price_changes)

    #macd0, = plt.plot(np.array(price_changes) / avg_price, label='PRICEDIFF')
    #vol0, = plt.plot((np.array(volume_changes) / avg_volume) * np.array(macd_diff[1:]), label='VOLDIFF')
    #ema4, = plt.plot(ema0["y"], label='EMA4')
    #macd0, = plt.plot(macd_data, label='MACD')
    #signal0, = plt.plot(macd_signal, label='SIG')
    #diff0, = plt.plot(macd_diff, label='DIFF')
    #plt.legend(handles=[macd0, signal0, diff0])
    #plot_emas_product(plt, 'LTC-BTC')

    #pc = gdax.PublicClient()
    #book = pc.get_product_order_book('BTC-USD', level=2)
    #for product in pc.get_products():
    #    print(product)

    #prices = prices_from_kline_data(klines)
    #ema12 = []
    #ema = EMA(30)
    #for price in prices:
    #    ema12.append(ema.update(price))
    #smma14 = []
    #smma = SMMA(14)
    #for price in prices:
    #    smma14.append(smma.update(price))
    #plt.subplot(223)
    #plt.plot(prices, label='prices')
    #plt.plot(ema12, label='EMA12')
    #plt.plot(smma14, label='SMMA14')

    #asks_x = []
    #asks_y = []
    #for ask in book['asks']:
    #    asks_x.append(float(ask[0]))
    #    asks_y.append(float(ask[1]) * float(ask[2]))
    #plt.subplot(224)
    #plt.plot(asks_x, asks_y, label='asks')

    plt.show()
