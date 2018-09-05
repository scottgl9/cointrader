#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.binance import client
from trader.config import *

def get_all_tickers(client):
    result = []
    for key, value in client.get_exchange_info().items():
        if key != 'symbols': continue
        for asset in value:
            #if asset['symbol'].endswith('USDT'): continue
            result.append(asset['symbol'])
    return result

if __name__ == '__main__':
    client = client.Client(MY_API_KEY, MY_API_SECRET)
    tickers = get_all_tickers(client)
    btc_usd_price = float(client.get_symbol_ticker(symbol='BTCUSDT')['price'])
    print("BTC/USDT={}".format(btc_usd_price))
    total_balance_usd = 0.0
    total_balance_btc = 0.0
    for accnt in client.get_account()['balances']:
        if float(accnt['free']) != 0.0 or float(accnt['locked']) != 0.0:
            price = 0.0
            price_usd = 0.0
            price_btc = 0.0
            if accnt['asset'] != 'BTC' and accnt['asset'] != 'USDT':
                symbol = "{}BTC".format(accnt['asset'])
                if symbol not in tickers:
                    continue
                price = float(client.get_symbol_ticker(symbol=symbol)['price'])
                total_amount = float(accnt['free']) + float(accnt['locked'])
                price_btc = price * total_amount
            elif accnt['asset'] != 'USDT':
                price = 1.0
                total_amount = float(accnt['free']) + float(accnt['locked'])
                price_btc = total_amount
            else:
                price = 1.0
                total_amount = float(accnt['free']) + float(accnt['locked'])
                price_btc = total_amount / btc_usd_price

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
