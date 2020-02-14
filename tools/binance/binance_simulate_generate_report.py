#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

import os.path

#try:
#    from trader.lib.native.Kline import Kline
#except ImportError:

from trader.TraderConfig import TraderConfig
import argparse
import logging
import re
import csv


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action='store', dest='strategy',
                        default='basic_signal_market_strategy',
                        help='name of strategy to use')

    parser.add_argument('-c', action='store', dest='cache_dir',
                        default='cache',
                        help='simulation cache directory')

    parser.add_argument('-o', action='store', dest='out_csv_file',
                        default='results.csv',
                        help='Simulation results CSV file')

    parser.add_argument('--currency', action='store', dest='currency',
                        default='',
                        help='currency to report on (default: all)')

    results = parser.parse_args()

    logFormatter = logging.Formatter("%(message)s")
    logger = logging.getLogger()

    config = TraderConfig("trader.ini")
    config.select_section('binance.simulate')

    #if not results.signal_names and not results.hourly_signal_names:
    #    parser.print_help()
    #    sys.exit(0)

    if results.strategy:
        config.set('strategy', results.strategy)

    strategy = config.get('strategy')


    fnames = ['strategy', 'dbname', 'signal', 'rt_hourly_signal', 'init_balance', 'profit']
    csvfile = open(results.out_csv_file, 'w', newline='')
    writer = csv.DictWriter(csvfile, fieldnames=fnames)
    writer.writeheader()

    base_cache_path = "{}/{}".format(results.cache_dir, strategy)
    for dbname in sorted(os.listdir(base_cache_path)):
        cache_path = "{}/{}".format(base_cache_path, dbname)
        for result_file in sorted(os.listdir(cache_path)):
            if not result_file.endswith('.txt'):
                continue
            result_file_path = "{}/{}".format(cache_path, result_file)
            with open(result_file_path, 'r') as f:
                m = re.search(r"(\d+).(\d+)%", f.read())
                if not m:
                    continue
                percent = m.group(0)
                parts = result_file.replace('.txt','').split('-')
                entry = {'strategy': strategy,
                         'dbname': dbname,
                         'signal': parts[0],
                         'rt_hourly_signal': parts[1],
                         'init_balance': parts[2],
                         'profit': percent
                         }
                writer.writerow(entry)
    csvfile.close()
