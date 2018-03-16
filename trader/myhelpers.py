#!/usr/bin/python

from trader.account import gdax
from datetime import datetime, timedelta
import numpy as np
import aniso8601


def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return float(total_seconds)

# simulate buys and sells in order to estimate profit from algorithm(s)
class AccountSimulate:
    def __init__(self, auth_client, name, currency='USD', quote_balance=100.0, base_balance=0.0):
        self.quote_balance=quote_balance
        self.base_balance=base_balance
    #def buy_limit(self, price, size, post_only=True):
    #def sell_limit(self, price, size, post_only=True):

# for gdax keep in mind historic rates are in reverse order
def retrieve_klines_24hrs(name):
    end = datetime.utcnow()
    start = (end - timedelta(hours=24))
    pc = gdax.PublicClient()
    rates = pc.get_product_historic_rates(name, start.isoformat(), end.isoformat(), 300)
    return rates[::-1]

def retrieve_klines_days(name, days=1):
    end = datetime.utcnow()
    start = (end - timedelta(days=days))
    pc = gdax.PublicClient()
    rates = pc.get_product_historic_rates(name, start.isoformat(), end.isoformat(), 900)
    return rates[::-1]

# for gdax keep in mind historic rates are in reverse order
def retrieve_klines_last_hour(name, hours=1):
    end = datetime.utcnow()
    start = (end - timedelta(hours=hours))
    pc = gdax.PublicClient()
    rates = pc.get_product_historic_rates(name, start.isoformat(), end.isoformat(), 60)
    return rates[::-1]

def prices_from_kline_data(klines):
    prices = []

    for i in range(0, len(klines) - 1):
        prices.append(klines[i][3])

    return prices

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
        y.append(float(kline[3]))

    emay = compute_ema_from_kline_prices(y, weight)
    return {"x": x, "y": emay}

def compute_ema_from_kline_prices(data, weight=26):
    ema = []
    prices = compute_sma_from_kline_prices(data, weight)
    k = 2.0 / (float(weight) * 24.0 + 1.0)
    last_price = float(prices[0])

    for i in range(1, len(prices) - 1):
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
            slopex = float(ema1["x"][i + 1]) - float(ema1["x"][i])
            if slopex != 0.0:
                slope1 = unit_price * (float(ema1prices[i + 1]) - float(ema1prices[i])) / slopex
                slope2 = (float(ema2prices[i + 1]) - float(ema2prices[i])) / slopex
                print(slope1)

            epoch = datetime.utcfromtimestamp(0)
            minutes = (epoch - datetime.fromtimestamp(ema1["x"][i] / 1000)).seconds / 60
            print("ema crossed down at %d %s" % (i, minutes))

        elif not mask[i] and mask[i + 1]:
            #slopex = datetime_to_float(ema1["x"][i + 2]) - datetime_to_float(ema1["x"][i])
            slopex = float(ema1["x"][i + 1]) - float(ema1["x"][i])
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

def query_price_last_minute(db):
    ret = []
    end = datetime.utcnow()
    start = (end - timedelta(minutes=1))
    result = db.LTC_collection.find({ "type": "match", "time": {"$gt": start.isoformat(), "$lte": end.isoformat()}}, {"time": 1, "price": 1, "_id": False})
    for ent in result:
        ret.append(float(ent['price']))
    return ret

def query_price_last_hour(db):
    x = []
    y = []
    end = datetime.utcnow()
    start = (end - timedelta(hours=1))
    result = db.LTC_collection.find({ "type": "match", "time": {"$gt": start.isoformat(), "$lte": end.isoformat()}}, {"time": 1, "price": 1, "_id": False})
    for ent in result:
        x.append(aniso8601.parse_datetime(ent['time']))
        y.append(float(ent['price']))
    return {"x":x, "y":y}

def query_price_last_day(db):
    x = []
    y = []
    end = datetime.utcnow()
    start = (end - timedelta(days=1))
    result = db.LTC_collection.find({ "type": "match", "time": {"$gt": start.isoformat(), "$lte": end.isoformat()}}, {"time": 1, "price": 1, "_id": False})
    for ent in result:
        x.append(aniso8601.parse_datetime(ent['time']).replace(tzinfo=None))
        y.append(float(ent['price']))
    return {"x":x, "y":y}

def compute_sma_last_hour(db, window=12):
    sma = []
    data = query_price_last_hour(db)
    prices = data["y"]
    for i in range(0, len(prices) - 1):
        if (i + window) >= len(prices): break
        value = prices[i]
        for j in range(1, window):
            value += prices[i+j]
        value /= float(window)
        sma.append(round(value, 2))
    return sma

def compute_sma_last_day(db, window=12, data=None):
    sma = []
    if data == None:
        data = query_price_last_day(db)
    prices = data["y"]
    for i in range(window, len(prices) - 1):
        #if (i + window) >= len(prices): break
        value = prices[i]
        for j in range(1, window):
            value += prices[i-j]
        value /= float(window)
        sma.append(round(value, 2))
    return {"x":data["x"][window:] ,"y":sma}

#  calculation (based on tick/day):
#  EMA = Price(t) * k + EMA(y) * (1 - k)
#  t = today, y = yesterday, N = number of days in EMA, k = 2 / (N+1)
def compute_ema_last_hour(db, weight=26, data=None):
    ema = []
    if data == None:
        data = compute_sma_last_day(db, weight, data) #query_price_last_day(db)
    times = np.array(data["x"])
    prices = data["y"]

    end = datetime.utcnow().replace(tzinfo=None)
    start = (end - timedelta(hours=1))
    mask = ((times > start) & (times < end))

    k = 2.0 / (float(weight) * 24.0 + 1.0)
    last_price = float(prices[0])

    for i in range(1, len(prices) - 1):
        last_price = float(prices[i] * k + last_price * (1.0 - k))
        if mask[i]:
            ema.append(last_price)
    return {"x":times[mask], "y":ema}

def find_price_crossover(db):
    data = query_price_last_hour(db)
    ema = compute_ema_last_hour(db, 12)
    prices = data["y"]
    emaprices = ema["y"]

    lastprice = prices[0]
    emalastprice = emaprices[0]
    last_gt_ema = lastprice > emalastprice
 
    for i in range(1, len(prices) - 1):
        if i > (len(emaprices) - 1): break;
        if emaprices[i] > prices[i] and last_gt_ema:
            print("price moved below ema at %d" % i)
        elif emaprices[i] < prices[i] and not last_gt_ema:
            print("price moved above ema at %d" % i)

        lastprice = prices[i]
        emalastprice = emaprices[i]
        last_gt_ema = lastprice > emalastprice

def find_emas_crossover(db):
    data = query_price_last_day(db)
    ema1 = compute_ema_last_hour(db, 12, data)
    ema2 = compute_ema_last_hour(db, 26, data)
    ema1prices = np.array(ema1["y"])
    ema2prices = np.array(ema2["y"])
    mask = ema1prices > ema2prices

    for i in range(0, len(mask) - 2):
        if mask[i] and not mask[i + 1]:
            slopex = datetime_to_float(ema1["x"][i + 2]) - datetime_to_float(ema1["x"][i])
            if slopex != 0.0:
                slope1 = (float(ema1prices[i + 2]) - float(ema1prices[i])) / slopex
                slope2 = (float(ema1prices[i + 2]) - float(ema1prices[i])) / slopex
                print(slope1)
                print(slope2)
            print("ema crossed down at %d" % i)

        elif not mask[i] and mask[i + 1]:
            slopex = datetime_to_float(ema1["x"][i + 2]) - datetime_to_float(ema1["x"][i])
            if slopex != 0.0:
                slope1 = (float(ema1prices[i + 2]) - float(ema1prices[i])) / slopex
                slope2 = (float(ema1prices[i + 2]) - float(ema1prices[i])) / slopex
                print(slope1)
                print(slope2)
            print("ema crossed up at %d" % i)