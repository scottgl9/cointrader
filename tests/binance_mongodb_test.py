#!/usr/bin/python

from pymongo import MongoClient
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from trader.binance.client import Client

from trader.config import *
client = Client(MY_API_KEY, MY_API_SECRET)
QUOTE_ASSET='BTC'

def unix_time_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds()) * 1000

# get sorted list of BTC symbols which have the largest 24 hr price change percentage
def get_btc_products(client):
    products = client.get_products()
    tickers = client.get_all_tickers()
    pdict = {}
    percents = {}
    volumes = {}

    for product in products.values()[0]:
        if 'quoteAsset' in product and product['quoteAsset'] == QUOTE_ASSET and product['active']:
            pdict[product['symbol']] = product
            print(product)
 
    for ticker in tickers:
        if ticker['symbol'].endswith(QUOTE_ASSET) == False: continue
        if ticker['symbol'] not in pdict.keys(): continue

        #fraction_movement = count_frames_direction_from_klines_name(ticker['symbol'])
        #print(fraction_movement)
        #if fraction_movement < 1.0: continue

        product = pdict[ticker['symbol']]
        percent = ((float(ticker['price']) - float(product['open'])) / float(product['open'])) * 100.0
        #if percent <= 0.0: continue
        #if float(ticker['price']) < (float(product['high']) + float(product['low'])) / 2.0: continue
        #percents[ticker['symbol']] = fraction_movement #round(percent, 2)
        volumes[ticker['symbol']] = float(product['volume'])

    return sorted(volumes.iteritems(), key=lambda (k,v): (v,k), reverse=True)

def get_account_balances(client):
    balances = {}
    tickers = client.get_all_tickers()
    for balance in client.get_account()['balances']:
        if 'free' not in balance: continue
        if float(balance['free']) == 0.0: continue
        balances[balance['asset']] = float(balance['free'])

        btcusdt = float(client.get_symbol_ticker(symbol=('%sUSDT' % QUOTE_ASSET))['price'])
        valuebtc = 1.0
        if balance['asset'] != QUOTE_ASSET and (balance['asset'] + QUOTE_ASSET) in tickers:
            valuebtc = float(client.get_symbol_ticker(symbol=(balance['asset'] + QUOTE_ASSET))['price'])
        balance_usd = float(balance['free']) * valuebtc * btcusdt
        print("%s balance %f (%f USD)" % (balance['asset'], float(balance['free']), balance_usd))
    return balances

# adjust prices for NAME/BTC to NAME/USD by multiplying by BTC/USDT
def adjust_kline_btc_usd(name, interval, time):
    klines_usd = client.get_historical_klines(('%sUSDT' % QUOTE_ASSET), interval, time)
    klines = client.get_historical_klines(name, interval, time)

    for i in range(0, len(klines) - 1):
        klines[i][1] = float(klines[i][1]) * float(klines_usd[i][1])
        klines[i][2] = float(klines[i][2]) * float(klines_usd[i][2])
        klines[i][3] = float(klines[i][3]) * float(klines_usd[i][3])
        klines[i][4] = float(klines[i][4]) * float(klines_usd[i][4])

    return klines

def prices_from_kline(name, time, usd=True):
    prices = []

    if usd:
        klines = adjust_kline_btc_usd(name, Client.KLINE_INTERVAL_1MINUTE, time)
    else:
        klines = client.get_historical_klines(name, Client.KLINE_INTERVAL_1MINUTE, time)

    for i in range(0, len(klines) - 1):
        prices.append(klines[i][1])

    return prices

def prices_from_kline_data(klines):
    prices = []

    for i in range(0, len(klines) - 1):
        prices.append(klines[i][1])

    return prices

def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return float(total_seconds)

def compute_ema_crossover_from_klines(ema1, ema2):
    if len(ema2["y"]) < len(ema1["y"]):
        ema1["y"] = ema1["y"][0:len(ema2["y"])]
    ema1prices = np.array(ema1["y"])
    ema2prices = np.array(ema2["y"])
    mask = ema1prices > ema2prices

    min_price = min(ema1prices)
    max_price = max(ema1prices)
    unit_price = float(len(ema1["x"])) / (max_price - min_price)

    for i in range(0, len(mask) - 2):
        if mask[i] and not mask[i + 1]:
            #slopex = datetime_to_float(ema1["x"][i + 2]) - datetime_to_float(ema1["x"][i])
            slopex = float(ema1["x"][i + 1]/1000) - float(ema1["x"][i]/1000)
            if slopex != 0.0:
                slope1 = unit_price * (float(ema1prices[i + 1]) - float(ema1prices[i])) / slopex
                slope2 = (float(ema2prices[i + 1]) - float(ema2prices[i])) / slopex
                print(slope1)

            epoch = datetime.utcfromtimestamp(0)
            minutes = (epoch - datetime.fromtimestamp(ema1["x"][i] / 1000)).seconds / 60
            print("ema crossed down at %d %s" % (i, minutes))

        elif not mask[i] and mask[i + 1]:
            #slopex = datetime_to_float(ema1["x"][i + 2]) - datetime_to_float(ema1["x"][i])
            slopex = float(ema1["x"][i + 1]/1000) - float(ema1["x"][i]/1000)
            if slopex != 0.0:
                slope1 = unit_price * (float(ema1prices[i + 1]) - float(ema1prices[i])) / slopex
                slope2 = (float(ema2prices[i + 1]) - float(ema2prices[i])) / slopex
                print(slope1)

            epoch = datetime.utcfromtimestamp(0)
            minutes = (epoch - datetime.fromtimestamp(ema1["x"][i] / 1000)).seconds / 60
            print("ema crossed up at %d %s" % (i, minutes))

def estimate_future_ema_crossover_from_klines(ema1, ema2):
    ema1_unit_price = float(len(ema1["x"])) / (max(ema1["y"]) - min(ema1["y"]))
    ema2_unit_price = float(len(ema2["x"])) / (max(ema2["y"]) - min(ema2["y"]))
    ema1_deltax = float(ema1["x"][-1]/1000) - float(ema1["x"][-2]/1000)
    ema1_deltay = ema1["y"][-1] - ema1["y"][-2]
    ema2_deltax = float(ema2["x"][-1]/1000) - float(ema2["x"][-2]/1000)
    ema2_deltay = ema2["y"][-1] - ema2["y"][-2]

    ema1_slope = ema1_unit_price * ema1_deltay / ema1_deltax
    ema2_slope = ema2_unit_price * ema2_deltay / ema2_deltax
    print(ema1_slope)
    print(ema2_slope)

def compute_sma_from_kline_prices(data, window=12):
    sma = []
    prices = []
    age = 0
    sum = 0.0

    for i in range(0, len(data) - 1):
        if len(prices) < window:
            tail = 0 #float(data[i])
            prices.append(float(data[i]))
        else:
            tail = prices[age]
            prices[age] = float(data[i])
        sum += float(data[i]) - tail
        sma.append(sum / float(len(prices)))
        age = (age + 1) % window
    return sma #[window:]

def compute_ema_dict_from_klines(klines, weight=26):
    x = []
    y = []
    for kline in klines:
        x.append(int(kline[0]))
        y.append(float(kline[1]))

    emay = compute_ema_from_kline_prices(y, weight)
    return {"x": x, "y": emay}

def compute_ema_from_kline_prices(data, weight=26):
    ema = []
    prices = compute_sma_from_kline_prices(data, weight)
    k = 2.0 / (float(weight) * 24.0 + 1.0)
    last_price = float(prices[0])

    for i in range(0, len(prices) - 1):
        last_price = float(prices[i] * k + last_price * (1.0 - k))
        ema.append(last_price)
    return ema

def compute_smma_from_kline_prices(klines, weight=14):
    smma = []
    #prices = prices_from_kline_data(klines)
    sma = compute_sma_from_kline_prices(klines, weight)
    #for i in range(0, weight - 1):
    #    smma.append(float(klines[i][4]))
    result = sma[0]
    for i in range(1, len(sma) - 1):
        value = sma[i]
        result = (result * (weight - 1.0) + value) / weight
        smma.append(result)
    return smma

def count_frames_direction_from_klines_name(name):
    klines = client.get_historical_klines(name, Client.KLINE_INTERVAL_1MINUTE,  "2 hours ago UTC")
    return count_frames_direction_from_klines(klines)

def count_frames_direction_from_klines(klines):
    upcnt = 0
    downcnt = 0
    upchange = 0.0
    downchange = 0.0

    for kline in klines:
        openprice = float(kline[1])
        closeprice = float(kline[4])
        if closeprice > openprice:
            upcnt += 1
            upchange += closeprice - openprice
        elif closeprice < openprice:
            downcnt += 1
            downchange += openprice - closeprice

    return float(upchange) - float(downchange) #100.0 * float(upcnt) / (float(upcnt) + float(downcnt))

def compute_rsi_from_klines(klines):
    rsi = []
    avgU = []
    avgD = []
    #klines = adjust_kline_btc_usd(name, Client.KLINE_INTERVAL_1MINUTE, time)
    #klines = client.get_historical_klines(name, Client.KLINE_INTERVAL_1MINUTE, time)
    #smma = compute_smma_from_kline_prices(klines)
    u = 0.0
    d = 0.0
    counter = 0
    lastcloseprice = 0.0

    prices = prices_from_kline_data(klines)
    smma = compute_smma_from_kline_prices(prices)

    for closeprice in smma:
        #closeprice = float(kline[4])

        if lastcloseprice == 0.0:
            lastcloseprice = closeprice
            continue

        if closeprice > lastcloseprice:
            u = closeprice - lastcloseprice
            d = 0.0
        elif closeprice < lastcloseprice:
            u = 0.0
            d = lastcloseprice - closeprice
        avgU.append(u)
        avgD.append(d)

        counter += 1

        #if counter != 0 and (counter % 14) != 0: continue

        avgU_result = 0.0
        for value in avgU:
            avgU_result += value
        if len(avgU) != 0: avgU_result /= float(len(avgU))

        avgD_result = 0.0
        for value in avgD:
            avgD_result += value
        if len(avgD) != 0: avgD_result /= float(len(avgD))

        if (avgD_result == 0.0 and avgU_result != 0.0):
            rsi.append(100.0)
        elif avgD_result == 0.0:
            rsi.append(0.0)
        else:
            rs = avgU_result / avgD_result
            rsi.append(100.0 - (100.0 / (1.0 + rs)))
        #if len(avgU) > 14.0: avgU = avgU[1:]
        #if len(avgD) > 14.0: avgD = avgD[1:]

    return rsi

def plot_emas_product_klines(client, plt, product, klines):
    #klines = client.get_historical_klines(product, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    ema1 = compute_ema_dict_from_klines(klines, 12)
    ema2 = compute_ema_dict_from_klines(klines, 26)
    compute_ema_crossover_from_klines(ema1, ema2)
    estimate_future_ema_crossover_from_klines(ema1, ema2)
    prices = prices_from_kline_data(klines)
    symprice, = plt.plot(prices, label=product)
    smma12, = plt.plot(compute_smma_from_kline_prices(prices, 12), label='SMMA12')
    ema12, = plt.plot(ema1["y"], label='EMA12')
    ema26, = plt.plot(ema2["y"], label='EMA26')
    ema50, = plt.plot(compute_ema_from_kline_prices(prices, 50), label='EMA50')
    plt.legend(handles=[symprice, smma12, ema12, ema26, ema50])

if __name__ == '__main__':
    mongo_client = MongoClient('mongodb://localhost:27017/')

    #client = Client(MY_API_KEY, MY_API_SECRET)
    #prices = client.get_all_tickers()
    #print(prices)
    db = mongo_client.cryptocurrency_database
    XRP_collection = db.XRP_collection
    #print(db.XRP_collection.count())

    products = get_btc_products(client)
    product = products[0][0]

    #for (name, percent) in products:
    #    print(name + str(percent))
    #    #print(count_frames_direction_from_klines_name(name))
    #product="DGD" + QUOTE_ASSET
    #product = products[0][0]

    print(get_account_balances(client))

    #klines = client.get_historical_klines(product, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    #print(count_frames_direction_from_klines(klines))
    #ema1 = compute_ema_dict_from_klines(klines, 12)
    #ema2 = compute_ema_dict_from_klines(klines, 26)
    #compute_ema_crossover_from_klines(ema1, ema2)

    klines = client.get_historical_klines(product, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    plt.figure(1)
    plt.subplot(211)
    plot_emas_product_klines(client, plt, product, klines)
    plt.subplot(212)
    plt.plot(compute_rsi_from_klines(klines))
    plt.show()
    #find_price_crossover(db)
    #find_emas_crossover(db)
    #pd.DataFrame(query_price_last_hour(db))
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
