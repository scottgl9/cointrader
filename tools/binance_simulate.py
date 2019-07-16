#!/usr/bin/python

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
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader

#try:
#    from trader.lib.native.Kline import Kline
#except ImportError:
from trader.lib.struct.Kline import Kline

from trader.account.AccountBinance import AccountBinance
from trader.TraderConfig import TraderConfig
from trader.config import *
import argparse
import logging
import json


def create_db_connection(filename):
    try:
        conn = sqlite3.connect(filename, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(e)

    return None


def create_table(c, name, id):
    cur = c.cursor()
    if id == 'ts':
        sql = """CREATE TABLE IF NOT EXISTS {} (ts INTEGER)""".format(name)
    else:
        sql = """CREATE TABLE IF NOT EXISTS {} ('{}' REAL)""".format(name, id)
    cur.execute(sql)
    c.commit()


def add_column(c, name, id):
    cur = c.cursor()
    if id == 'ts':
        sql = """ALTER TABLE {} ADD COLUMN 'ts' INTEGER;""".format(name)
    else:
        sql = """ALTER TABLE {} ADD COLUMN '{}' REAL;""".format(name, id)
    cur.execute(sql)
    c.commit()


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


def simulate(conn, config, logger, simulate_db_filename=None):
    start_time = time.time()
    c = conn.cursor()
    c.execute("SELECT * FROM miniticker ORDER BY E ASC")

    if not os.path.exists("asset_info.json") or not os.path.exists("asset_detail.json"):
        client = Client(MY_API_KEY, MY_API_SECRET)
    else:
        client = None

    accnt = AccountBinance(client,
                           simulation=True,
                           logger=logger,
                           simulate_db_filename=simulate_db_filename)
    accnt.load_info_all_assets()
    accnt.load_detail_all_assets()

    if not config.section_exists('binance.simulate'):
        print("Section binance.simulate does not exist")
        sys.exit(-1)

    config.select_section('binance.simulate')
    btc_balance = config.get('BTC')
    eth_balance = config.get('ETH')
    bnb_balance = config.get('BNB')

    if btc_balance:
        accnt.update_asset_balance('BTC', float(btc_balance), float(btc_balance))

    if eth_balance:
        accnt.update_asset_balance('ETH', float(eth_balance), float(eth_balance))

    if bnb_balance:
        accnt.update_asset_balance('BNB', float(bnb_balance), float(bnb_balance))

    multitrader = MultiTrader(client,
                              accnt=accnt,
                              logger=logger,
                              config=config)

    initial_balances = multitrader.accnt.balances
    print(initial_balances)

    found = False

    initial_btc_total = 0.0
    initial_bnb_total = 0.0

    first_ts = None
    last_ts = None

    kline = None
    cache_filename = simulate_db_filename

    #if os.path.exists(cache_filename):
    #    logger.info("Loading indicator cache {}".format(cache_filename))
    #    cache_db = create_db_connection(cache_filename)
    #    #cache_db = create_db_connection(':memory:')
    #    #cache_db.backup(cache_db_file)
    #    #cache_db_file.close()
    #else:
    #    cache_db = create_db_connection(cache_filename)
    cache_db = None

    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}

        if not first_ts:
            first_ts = datetime.utcfromtimestamp(int(msg['E'])/1000)
        else:
            last_ts = datetime.utcfromtimestamp(int(msg['E'])/1000)

        if not found:
            if multitrader.accnt.total_btc_available():
                found = True
                total_btc = multitrader.accnt.get_total_btc_value()
                initial_btc_total = total_btc
                initial_bnb_total = multitrader.accnt.get_total_bnb_value()
                multitrader.update_initial_btc()

        # if balance of USDT less than 20.0, then ignore all symbols ending in USDT
        #if msg['s'].endswith("USDT"):
        #    minqty = 20.0
        #    balance = accnt.get_asset_balance("USDT")["balance"]
        #    if balance < minqty:
        #        continue

        if not kline:
            kline = Kline(symbol=msg['s'],
                          open=float(msg['o']),
                          close=float(msg['c']),
                          low=float(msg['l']),
                          high=float(msg['h']),
                          volume_base=float(msg['v']),
                          volume_quote=float(msg['q']),
                          ts=int(msg['E']))
        else:
            kline.symbol = msg['s']
            kline.open = float(msg['o'])
            kline.close = float(msg['c'])
            kline.low = float(msg['l'])
            kline.high= float(msg['h'])
            kline.volume_base = float(msg['v'])
            kline.volume_quote = float(msg['q'])
            kline.volume = kline.volume_quote
            kline.ts = int(msg['E'])

        multitrader.process_message(kline, cache_db=cache_db)

    if cache_db:
        cache_db.commit()
        cache_db.close()

    logger.info("\nTrade Symbol Profits:")
    final_btc_total = multitrader.accnt.get_total_btc_value()
    final_bnb_total = multitrader.accnt.get_total_bnb_value()
    total_pprofit = 0
    total_bnb_pprofit = 0
    if initial_btc_total:
        total_pprofit = round(100.0 * (final_btc_total - initial_btc_total) / initial_btc_total, 2)

    if initial_bnb_total and final_bnb_total:
        total_bnb_pprofit = round(100.0 * (final_bnb_total - initial_bnb_total) / initial_bnb_total, 2)

    for pair in multitrader.trade_pairs.values():
        for signal in pair.get_signals():
            if signal.buy_price != 0.0:
                buy_price = float(signal.buy_price)
                last_price = float(pair.last_price)
                symbol = pair.ticker_id
                pprofit = round(100.0 * (last_price - buy_price) / buy_price, 2)
                logger.info("{} ({}): {}%".format(symbol, signal.id, pprofit))

    total_time_hours = (last_ts - first_ts).total_seconds() / (60 * 60)
    logger.info("\nResults:")
    logger.info("Total Capture Time:\t{} hours".format(round(total_time_hours, 2)))
    logger.info("Initial BTC total:\t{}".format(initial_btc_total))
    logger.info("Final BTC total:\t{}".format(final_btc_total))
    if initial_bnb_total:
        logger.info("Initial BNB total:\t{}".format(initial_bnb_total))
    if final_bnb_total:
        logger.info("Final BNB total:\t{}".format(final_bnb_total))
    logger.info("Percent Profit (BTC): \t{}%".format(total_pprofit))
    logger.info("Percent Profit (BNB): \t{}%".format(total_bnb_pprofit))

    run_time = int(time.time() - start_time)
    print("Simulation Run Time:\t{} seconds".format(run_time))
    print(multitrader.order_handler.trade_balance_handler.get_balances())

    min_tickers = accnt.get_min_tickers()
    max_tickers = accnt.get_max_tickers()
    end_tickers = accnt.get_tickers()

    return multitrader.get_stored_trades(), end_tickers, min_tickers, max_tickers, total_pprofit, initial_btc_total


def get_detail_all_assets(client):
    return client.get_asset_details()


def get_info_all_assets(client):
    assets = {}
    for key, value in client.get_exchange_info().items():
        if key != 'symbols':
            continue
        for asset in value:
            minNotional = ''
            minQty = ''
            tickSize = ''
            stepSize = ''
            for filter in asset['filters']:
                if 'minQty' in filter:
                    minQty = filter['minQty']
                if 'tickSize' in filter:
                    tickSize = filter['tickSize']
                if 'stepSize' in filter:
                    stepSize = filter['stepSize']
                if 'minNotional' in filter:
                    minNotional = filter['minNotional']

            assets[asset['symbol']] = {'minQty': minQty,
                                       'tickSize': tickSize,
                                       'stepSize': stepSize,
                                       'minNotional': minNotional
                                       }

    return assets


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

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
                        default='binance_hourly_klines.db',
                        help='binance hourly klines DB file')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    if not os.path.exists(results.cache_dir):
        os.mkdir(results.cache_dir)

    #logFormatter = logging.Formatter("[%(levelname)-5.5s]  %(message)s")
    logFormatter = logging.Formatter("%(message)s")
    logger = logging.getLogger()

    config = TraderConfig("trader.ini")
    config.select_section('binance.simulate')
    strategy = config.get('strategy')
    signal_name = config.get('signals')

    if results.strategy:
        strategy = results.strategy

    if results.signal_name:
        signal_name = results.signal_name

    if results.hourly_signal_name:
        config.set('hourly_signal', results.hourly_signal_name)

    trade_cache = {}

    trade_cache_name = "{}-{}".format(strategy, signal_name)

    trade_log_filename = results.filename.replace(".db", "_{}.log".format(trade_cache_name))
    trade_log_filepath = os.path.join(results.cache_dir, trade_log_filename)

    trade_result_filename = results.filename.replace(".db", "_result_{}.txt".format(trade_cache_name))
    trade_result_filepath = os.path.join(results.cache_dir, trade_result_filename)

    # remove old trade log before re-running
    if os.path.exists(trade_log_filepath):
        os.remove(trade_log_filepath)

    fileHandler = logging.FileHandler(trade_log_filepath)
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    conn = sqlite3.connect(results.filename)

    # start the Web API
    #thread = threading.Thread(target=WebThread, args=(strategy,))
    #thread.daemon = True
    #thread.start()

    # if we already ran simulation, load the results
    trade_cache_filename = os.path.join(results.cache_dir, results.filename.replace('.db', '.json'))
    if os.path.exists(trade_cache_filename):
        logger.info("Loading {}".format(trade_cache_filename))
        with open(trade_cache_filename, "r") as f:
            trade_cache = json.loads(str(f.read()))

    logger.info("Running simulate with {} signal {}".format(results.filename, signal_name))

    hourly_kline_db_file = results.hourly_klines_db_file

    try:
        simulate_db_filename = os.path.join(results.cache_dir, os.path.basename(results.filename))
        print(simulate_db_filename)
        trades, end_tickers, min_tickers, max_tickers, total_pprofit, initial_btc_total = simulate(conn, config, logger, simulate_db_filename)
    except (KeyboardInterrupt, SystemExit):
        logger.info("CTRL+C: Exiting....")
        conn.close()
        sys.exit(0)

    with open(trade_cache_filename, "w") as f:
        if 'end_tickers' not in trade_cache.keys():
            trade_cache['end_tickers'] = end_tickers
        if 'max_tickers' not in trade_cache.keys():
            trade_cache['max_tickers'] = max_tickers
        if 'min_tickers' not in trade_cache.keys():
            trade_cache['min_tickers'] = min_tickers

        trade_cache[trade_cache_name] = {}
        trade_cache[trade_cache_name]['trades'] = trades
        f.write(json.dumps(trade_cache, f, indent=4, sort_keys=True))

    with open(trade_result_filepath, "w") as f:
        #trade_result = process_trade_cache(trades, end_tickers)
        #for symbol in sorted(trade_result):
        #    results = sorted(trade_result[symbol])
        #    f.write("{}: {}\n".format(symbol, results))
        f.write("Initial BTC Total: {}\n".format(initial_btc_total))
        f.write("Total Profit: {}%".format(total_pprofit))

