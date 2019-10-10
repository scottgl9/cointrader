#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

import os.path
import time
import sqlite3
from datetime import datetime
import sys
from trader.MultiTrader import MultiTrader
from trader.lib.struct.Kline import Kline
from trader.lib.struct.MarketMessage import MarketMessage
from trader.account.AccountBinance import AccountBinance
from trader.TraderConfig import TraderConfig
from trader.config import *
import argparse
import logging
import json


def process_trade_cache(trades, end_tickers):
    trade_info = {}
    for symbol, info in trades.items():
        for trade in info:
            sell_price = trade['price']
            type = trade['type']
            if type != 'sell':
                continue

            buy_price = trade['buy_price']

            # sell trade occurred, so calculate percent profit
            percent = round(100.0 * (sell_price - buy_price) / buy_price, 2)
            if symbol not in trade_info:
                trade_info[symbol] = [percent]
            else:
                trade_info[symbol].append(percent)

        # more buy trades than sell trades, so compute profit of last buy order
        if (len(info) & 1) != 0:
            buy_price = info[-1]['price']
            sell_price = end_tickers[symbol]
            percent = round(100.0 * (sell_price - buy_price) / buy_price, 2)
            if symbol not in trade_info:
                trade_info[symbol] = [percent]
            else:
                trade_info[symbol].append(percent)

    return trade_info


def simulate(config, logger, start_date, end_date):
    start_time = time.time()

    client = None
    accnt = AccountBinance(client,
                           simulation=True,
                           logger=logger)
    accnt.load_exchange_info()

    if not config.section_exists('binance.simulate'):
        print("Section binance.simulate does not exist")
        sys.exit(-1)

    # set balances from config
    balances = config.get_section_field_options(field='balance')
    for key, value in balances.items():
        accnt.update_asset_balance(key, float(value), float(value))

    multitrader = MultiTrader(client,
                              accnt=accnt,
                              logger=logger,
                              config=config)

    initial_balances = multitrader.accnt.balances
    print(initial_balances)

    start_dt = datetime.strptime(start_date, '%m/%d/%Y')
    end_dt = datetime.strptime(end_date, '%m/%d/%Y')
    start_ts = int(accnt.seconds_to_ts(time.mktime(start_dt.timetuple())))
    end_ts = int(accnt.seconds_to_ts(time.mktime(end_dt.timetuple())))
    kdb = multitrader.kdb
    #symbols = accnt.get_exchange_pairs()
    table_names = kdb.get_table_list()
    symbol_klines = {}

    first_ts = 0
    last_ts = 0

    symbols = []
    for name in table_names:
        symbol = accnt.get_symbol_hourly_table(name)
        klines = kdb.get_klines(symbol, start_ts, end_ts)
        if not len(klines):
            continue
        cur_first_ts = klines[0].ts
        cur_last_ts = klines[-1].ts
        if not first_ts or cur_first_ts < first_ts:
            first_ts = cur_first_ts
        if cur_last_ts > last_ts:
            last_ts = cur_last_ts
        symbols.append(symbol)
        symbol_klines[symbol] = klines

    found = False

    initial_total = 0.0

    mmsg = None
    profit_mode = config.get('trader_profit_mode')

    cur_ts = first_ts

    while cur_ts <= last_ts:
        for symbol in symbols:
            if not found:
                if profit_mode == 'BTC' and multitrader.accnt.total_btc_available():
                    found = True
                    initial_total = multitrader.accnt.get_total_btc_value()
                    multitrader.update_initial_currency()

            kline = symbol_klines[symbol][0]
            if kline.ts != cur_ts:
                continue
            if not mmsg:
                kline.symbol = symbol
                mmsg = MarketMessage(symbol, msg_type=MarketMessage.TYPE_DB_KLINE_MSG, kline=kline)
            else:
                kline.symbol = symbol
                mmsg.update(kline=kline)
            multitrader.process_market_message(mmsg)
            symbol_klines[symbol].remove(kline)
        cur_ts += int(accnt.hours_to_ts(1))

    logger.info("\nTrade Symbol Profits:")
    if profit_mode == 'BTC':
        final_total = multitrader.accnt.get_total_btc_value()
    elif profit_mode == 'BNB':
        final_total = multitrader.accnt.get_total_bnb_value()
    else:
        final_total = 0

    total_pprofit = 0

    if initial_total:
        total_pprofit = round(100.0 * (final_total - initial_total) / initial_total, 2)

    for pair in multitrader.trade_pairs.values():
        for signal in pair.get_signals():
            if signal.buy_price != 0.0:
                buy_price = float(signal.buy_price)
                last_price = float(pair.last_price)
                symbol = pair.ticker_id
                pprofit = round(100.0 * (last_price - buy_price) / buy_price, 2)
                logger.info("{} ({}): {}%".format(symbol, signal.id, pprofit))

    #total_time_hours = (last_ts - first_ts).total_seconds() / (60 * 60)
    logger.info("\nResults:")
    #logger.info("Total Capture Time:\t{} hours".format(round(total_time_hours, 2)))
    logger.info("Initial {} total:\t{}".format(profit_mode, initial_total))
    logger.info("Final {} total:\t{}".format(profit_mode, final_total))
    logger.info("Percent Profit ({}): \t{}%".format(profit_mode, total_pprofit))

    run_time = int(time.time() - start_time)
    print("Simulation Run Time:\t{} seconds".format(run_time))
    print(multitrader.order_handler.trade_balance_handler.get_balances())

    min_tickers = accnt.get_min_tickers()
    max_tickers = accnt.get_max_tickers()
    end_tickers = accnt.get_tickers()

    return multitrader.get_stored_trades(), end_tickers, min_tickers, max_tickers, total_pprofit, initial_total


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', action='store', dest='strategy',
                        default='',
                        help='name of strategy to use')

    parser.add_argument('-g', action='store', dest='signal_name',
                        default='',
                        help='name of signal to use')

    parser.add_argument('-r', action='store', dest='hourly_signal_name',
                        default='',
                        help='name of hourly signal to use')

    parser.add_argument('-c', action='store', dest='cache_dir',
                        default='cache',
                        help='simulation cache directory')

    parser.add_argument('-k', action='store', dest='hourly_klines_db_file',
                        default='binance_hourly_klines_BTC.db',
                        help='binance hourly klines DB file')

    parser.add_argument('--start-date', action='store', dest='start_date',
                        default='',
                        help='Start date for hourly simulation')

    parser.add_argument('--end-date', action='store', dest='end_date',
                        default='',
                        help='End date for hourly simulation')

    parser.add_argument('-d', action='store_true', dest='disable_caching',
                        default=True,
                        help='Disable caching results for this simulation run')

    results = parser.parse_args()

    if not os.path.exists(results.cache_dir):
        os.mkdir(results.cache_dir)

    if not results.start_date or not results.end_date:
        parser.print_help()
        sys.exit(0)

    start_date = results.start_date
    end_date = results.end_date

    logFormatter = logging.Formatter("%(message)s")
    logger = logging.getLogger()

    config = TraderConfig("trader.ini", exchange='binance')
    config.select_section('binance.simulate')

    if results.strategy:
        config.set('strategy', results.strategy)

    if results.signal_name:
        config.set('signals', results.signal_name)

    if results.hourly_signal_name:
        config.set('rt_hourly_signal', results.hourly_signal_name)

    strategy = config.get('strategy')
    signal_name = config.get('signals')
    hourly_name = config.get('rt_hourly_signal')
    disable_caching = results.disable_caching

    if disable_caching:
        trade_cache_name = ""
        trade_log_path = ""
        trade_result_path = ""
        trade_json_path = ""
        print("Caching of results to {} DISABLED".format(results.cache_dir))
    else:
        # create folder for strategy name in cache
        cache_path = "{}/{}".format(results.cache_dir, strategy)
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)

        cache_path = "{}/{}".format(cache_path, results.filename.replace(".db", ""))
        if not disable_caching and not os.path.exists(cache_path):
            os.mkdir(cache_path)
        trade_cache_name = "{}-{}".format(signal_name, hourly_name)
        trade_log_path = "{}/{}.log".format(cache_path, trade_cache_name)
        trade_result_path = "{}/{}.txt".format(cache_path, trade_cache_name)
        trade_json_path = "{}/trades.json".format(cache_path)

    trade_cache = {}

    # if caching disabled, do not write to log file
    if not disable_caching:
        # remove old trade log before re-running
        if os.path.exists(trade_log_path):
            os.remove(trade_log_path)

        fileHandler = logging.FileHandler(trade_log_path)
        fileHandler.setFormatter(logFormatter)
        logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    # if caching enabled and we already ran simulation, load the results
    if not disable_caching and os.path.exists(trade_json_path):
        logger.info("Loading {}".format(trade_json_path))
        with open(trade_json_path, "r") as f:
            try:
                trade_cache = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                logger.warn("Failed to load {}".format(trade_json_path))

    logger.info("Running hourly simulate with signal {}".format(signal_name))

    hourly_kline_db_file = results.hourly_klines_db_file

    try:
        trades, end_tickers, min_tickers, max_tickers, total_pprofit, initial_total = simulate(config, logger, start_date, end_date)
    except (KeyboardInterrupt, SystemExit):
        logger.info("CTRL+C: Exiting....")
        sys.exit(0)

    # caching results enabled, so save results in cache
    if not disable_caching:
        with open(trade_json_path, "w") as f:
            if 'end_tickers' not in trade_cache.keys():
                trade_cache['end_tickers'] = end_tickers
            if 'max_tickers' not in trade_cache.keys():
                trade_cache['max_tickers'] = max_tickers
            if 'min_tickers' not in trade_cache.keys():
                trade_cache['min_tickers'] = min_tickers

            trade_cache[trade_cache_name] = {}
            trade_cache[trade_cache_name]['trades'] = trades
            f.write(json.dumps(trade_cache, indent=4, sort_keys=True))

        profit_mode = config.get('trader_profit_mode')

        with open(trade_result_path, "w") as f:
            f.write("Initial {} Total: {}\n".format(profit_mode, initial_total))
            f.write("Total Profit: {}%\n".format(total_pprofit))
