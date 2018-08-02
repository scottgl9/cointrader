#!/usr/bin/python

from trader.account.yobit import YoBit
from trader.config import *

def get_price(client, base, currency):
    ticker_id = "{}_{}".format(base, currency)
    result = client.ticker(ticker_id)
    return float(result[ticker_id]['last'])

if __name__ == '__main__':
    client = YoBit(api_key=YOBIT_API_KEY, api_secret=YOBIT_API_SECRET)
    #print(client.info())

    funds = client.get_info()['return']['funds']
    #print(funds)

    for key, value in funds.items():
        price_usd = get_price(client, key, 'usd')
        if key != 'btc':
            price_btc = get_price(client, key, 'btc')
            print("{} = {} ({} USD, {} BTC)".format(key, value, float(value) * price_usd, float(value) * price_btc))
