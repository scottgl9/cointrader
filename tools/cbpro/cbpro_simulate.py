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
from trader.lib.struct.Exchange import Exchange
from trader.account.cbpro.AccountCoinbasePro import AccountCoinbasePro
from trader.TraderConfig import TraderConfig
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
    c.execute("SELECT * FROM miniticker ORDER BY ts ASC")

    client = None
    accnt = AccountCoinbasePro(client,
                               simulate=True,
                               logger=logger,
                               simulate_db_filename=simulate_db_filename)
    accnt.load_exchange_info()

    if not config.section_exists('cbpro.simulate'):
        print("Section cbpro.simulate does not exist")
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

    found = False

    initial_total = 0.0

    first_ts = None
    last_ts = None

    kline = None
    mmsg = None
    profit_mode = config.get('trader_profit_mode')

    last_close = 0

    for row in c:
        msg = {'ts': row[0], 'p': row[1], 'ask': row[2], 'bid': row[3],
               'q': row[4], 's': row[5], 'buy': row[6]}

        if not first_ts:
            first_ts = datetime.utcfromtimestamp(int(msg['ts']))
        else:
            last_ts = datetime.utcfromtimestamp(int(msg['ts']))

        if not found:
            if profit_mode == 'BTC' and multitrader.accnt.total_btc_available():
                found = True
                initial_total = multitrader.accnt.get_total_btc_value()
                multitrader.update_initial_currency()

        if not kline or not msg:
            kline = Kline(symbol=msg['s'],
                          open=last_close,
                          close=float(msg['p']),
                          low=float(msg['bid']),
                          high=float(msg['ask']),
                          volume=float(msg['q']),
                          ts=int(msg['ts']),
                          exchange_type=Exchange.EXCHANGE_CBPRO))
            mmsg = MarketMessage(kline.symbol, msg_type=MarketMessage.TYPE_WS_MSG, kline=kline)
        else:
            kline.symbol = msg['s']
            kline.open = last_close
            kline.close = float(msg['p'])
            kline.low = float(msg['bid'])
            kline.high= float(msg['ask'])
            kline.volume = float(msg['q'])
            kline.ts = int(msg['ts'])
            mmsg.update(kline=kline)

        last_close = kline.close

        multitrader.process_market_message(mmsg)

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

    total_time_hours = (last_ts - first_ts).total_seconds() / (60 * 60)
    logger.info("\nResults:")
    logger.info("Total Capture Time:\t{} hours".format(round(total_time_hours, 2)))
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
    parser.add_argument('-f', action='store', dest='filename',
                        default='db/cbpro_database.miniticker_collection_09132019.db',
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
                        default='cbpro_hourly_klines.db',
                        help='binance hourly klines DB file')

    parser.add_argument('-d', action='store_true', dest='disable_caching',
                        default=True,
                        help='Disable caching results for this simulation run')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    if not os.path.exists(results.cache_dir):
        os.mkdir(results.cache_dir)

    logFormatter = logging.Formatter("%(message)s")
    logger = logging.getLogger()

    config = TraderConfig("trader.ini", exchange='cbpro')
    config.select_section('cbpro.simulate')

    # set trader_mode to realtime
    config.set('trader_mode', 'realtime')

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

    conn = sqlite3.connect(results.filename)

    # if caching enabled and we already ran simulation, load the results
    if not disable_caching and os.path.exists(trade_json_path):
        logger.info("Loading {}".format(trade_json_path))
        with open(trade_json_path, "r") as f:
            try:
                trade_cache = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                logger.warn("Failed to load {}".format(trade_json_path))

    logger.info("Running simulate with {} signal {}".format(results.filename, signal_name))

    hourly_kline_db_file = results.hourly_klines_db_file

    try:
        simulate_db_filename = os.path.basename(results.filename)
        print(simulate_db_filename)
        trades, end_tickers, min_tickers, max_tickers, total_pprofit, initial_total = simulate(conn, config, logger, simulate_db_filename)
    except (KeyboardInterrupt, SystemExit):
        logger.info("CTRL+C: Exiting....")
        conn.close()
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
