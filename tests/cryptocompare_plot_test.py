#!/usr/bin/python

from trader.cryptocompare import CryptoCompare

if __name__ == '__main__':
    cc = CryptoCompare()
    #print(sorted(cc.get_coins_by_volume().iteritems(), key=lambda (k,v): (v,k), reverse=True))
    print(cc.get_coins_by_volume())
