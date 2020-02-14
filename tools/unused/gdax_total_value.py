#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

#from pymongo import MongoClient
from trader.account.gdax.authenticated_client import AuthenticatedClient
from trader.account.cbpro.coinbase.wallet import Client

from trader.config import *

if __name__ == '__main__':
        total_debit = 0.0
        total_sent = 0.0
        total_gdax = 0.0
        client = Client(COINBASE_KEY, COINBASE_SECRET)
        for account in client.get_accounts()['data']:
            for transaction in account.get_transactions()['data']:
                amount_usd = transaction['native_amount']['amount']
                amount = transaction['native_amount']['amount']
                subtitle = transaction['details']['subtitle']
                if "debit" in subtitle:
                    total_debit += float(amount_usd)
                elif subtitle == "To Bitcoin address":
                    total_sent -= float(amount_usd)
                elif subtitle == "To GDAX":
                    total_gdax -= float(amount_usd)
                elif subtitle == "From GDAX":
                    total_gdax -= float(amount_usd)
        balances = {}
        print("Total Debit: {} Sent: {} GDAX: {}".format(total_debit, total_sent, total_gdax))
        auth_client = AuthenticatedClient(GDAX_KEY, GDAX_SECRET, GDAX_PASS)
        pc = gdax.PublicClient()
        total = 0.0
        btc_value = 0.0
        for account in auth_client.get_accounts():
            if 'currency' not in account: continue
            price = 1.0
            if account['currency'] == 'BTC':
                btc_value += float(account['balance'])
            elif account['currency'] == 'USD':
                if float(account['balance']) > 10:
                    ticker = pc.get_product_ticker(product_id='%s-USD' % account['currency'])
            elif float(account['balance']) > 0.0:
                ticker = pc.get_product_ticker(product_id='%s-BTC' % account['currency'])
                btc_value += float(ticker['price']) * float(account['balance'])
            if account['currency'] != 'USD':
                ticker = pc.get_product_ticker(product_id='%s-USD' % account['currency'])
                if 'price' in ticker: price = float(ticker['price'])

                balances[account['currency']] = float(account['balance']) * price
                total += balances[account['currency']]
        print(balances)
        profit = total - total_gdax
        #btc_value = total / float(pc.get_product_ticker(product_id='BTC-USD')['price'])
        print("GDAX inital = {} current = {} profit = {}".format(total_gdax, total, profit))
        print("Account BTC value = {} BTC".format(btc_value))
