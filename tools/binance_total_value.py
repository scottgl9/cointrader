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
        if float(accnt['free']) != 0.0 or float(accnt['locked']) != 0.0:
            price = 0.0
            price_usd = 0.0
            price_btc = 0.0
            if accnt['asset'] != 'BTC':
                price = float(client.get_symbol_ticker(symbol="{}BTC".format(accnt['asset']))['price'])
                total_amount = float(accnt['free']) + float(accnt['locked'])
                price_btc = price * total_amount
            else:
                price = 1.0
                total_amount = float(accnt['free']) + float(accnt['locked'])
                price_btc = total_amount

            price_usd = price_btc * btc_usd_price
            total_balance_usd += price_usd
            total_balance_btc += price_btc
            usd_price = price * btc_usd_price
            if price_usd > 1.0:
                print("{} = {} ({} BTC {} USD)".format(accnt['asset'], total_amount, price_btc, price_usd))

    print("Total balance USD = {}, BTC={}".format(total_balance_usd, total_balance_btc))

    #client.get_ticker()
    #for ticker in client.get_all_tickers():
    #    print(ticker.items())
