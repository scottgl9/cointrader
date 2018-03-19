#!/usr/bin/python

from trader.account.binance import client
from config import *

if __name__ == '__main__':
    client = client.Client(MY_API_KEY, MY_API_SECRET)
    btc_usd_price = float(client.get_symbol_ticker(symbol='BTCUSDT')['price'])
    print(btc_usd_price)
    total_balance_usd = 0.0
    total_balance_btc = 0.0
    for accnt in client.get_account()['balances']:
        if float(accnt['free']) != 0.0:
            price = 1.0
            price_usd = 0.0
            price_btc = 0.0
            if accnt['asset'] != 'BTC':
                price = float(client.get_symbol_ticker(symbol="{}BTC".format(accnt['asset']))['price'])
                price_btc = price * (float(accnt['free']) + float(accnt['locked']))
                price_usd = price_btc *  btc_usd_price
                total_balance_usd += price_usd
                total_balance_btc += price_btc
                if price_usd > 0.01:
                    print("{} = {} ({} BTC {} USD)".format(accnt['asset'], accnt['free'], price_btc, price_usd))
            else:
                price_btc = (float(accnt['free']) + float(accnt['locked']))
                price_usd = price_btc *  btc_usd_price
                total_balance_usd += price_usd
                total_balance_btc += price_btc
                if price_usd > 0.01:
                    print("{} = {} ({} BTC {} USD)".format(accnt['asset'], accnt['free'], price_btc, price_usd))

    print("Total balance USD = {}, BTC={}".format(total_balance_usd, total_balance_btc))

    #client.get_ticker()
    #for ticker in client.get_all_tickers():
    #    print(ticker.items())
