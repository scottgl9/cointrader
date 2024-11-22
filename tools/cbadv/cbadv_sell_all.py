#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.cbadv.AccountCoinbaseAdvanced import AccountCoinbaseAdvanced
from trader.config import *

if __name__ == '__main__':
    accnt = AccountCoinbaseAdvanced(simulate=False)
    print("getting account balances")
    balances = accnt.get_account_balances()
    print(balances)
    #print(client.get_fees())
    print("USD Total: {} USD".format(accnt.get_account_total_value('USD')))
    accnt.get_exchange_info()
    #info = accnt.get_asset_info()
    #for i in info:
    #    print(i)
    for crypto, balance in balances.items():
        symbol = accnt.make_ticker_id(base=crypto, currency='USD')
        info = accnt.get_asset_info(symbol=symbol)
        if not info:
            continue
        if balance < info.min_qty:
            continue
        min_price = info.min_price

        # calculate the total value of the asset
        price = float(accnt.market.get_ticker(symbol))
        if not price:
            continue
        value = balance * price
        if value < min_price:
            #print(f"{crypto} currency_value < min_price: {value} < {min_price}")
            continue

        sell_size = accnt.round_quantity_symbol(symbol=symbol, size=balance)

        try:
            print(accnt.sell_market(ticker_id=symbol, size=sell_size))
            print(f"selling {crypto}: balance={balance} price={price} currency_value={value}")
        except:
            pass