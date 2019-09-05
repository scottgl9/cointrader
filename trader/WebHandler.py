from flask import Flask, render_template, json, request,redirect,session,jsonify
from flask.logging import *
import threading
import sys
import json
import logging

app = Flask(__name__)
#app.logger.removeHandler(app.logger.disabled)
global_running_flag = True

def WebThread(mtrader=None):
    if not mtrader:
        print("failed to load multitrader")
    elif mtrader:
        print("multitrader loaded")

    @app.route('/')
    def index():
        return render_template('status.html')

    @app.route('/basic')
    def basic():
        return render_template('basic.html')

    @app.route('/get_multi_trader_status')
    def get_multi_trader_status():
        return mtrader.strategy_name

    @app.route('/shutdown_trader')
    def shutdown_trader():
        global global_running_flag
        global_running_flag = False
        return "Shutting down..."

    #@app.route('/update_stats')
    #def update_stats():
    #    page = str('')
    #   page += trader.html_run_stats()
    #    page += trader.accnt.html_run_stats()
    #    #page += trader.order_handler.html_run_stats()
    #    return page

    # get last 50 prices
    #@app.route('/get_prices')
    #def get_prices():
    #    #trader.prev_last_50_prices = trader.last_50_prices
    #    return str(trader.last_50_prices)[1:-1]

    # get only new prices since last request
    #@app.route('/update_prices')
    #def update_prices():
    #    count = trader.count_prices_added
    ##    total_count = len(trader.last_50_prices)
    #   prices_added = trader.last_50_prices[total_count - count:]
    #   #if len(prices_added) != 0:
    #   #    print(prices_added)
    #    trader.clear_price_counter()
    #    return str(prices_added)[1:-1]

    #@app.route('/get_24hr_stats')
    #def get_24hr_stats():
    #    stats = trader.accnt.get_24hr_stats(ticker_id=trader.ticker_id)
    #    jsstats = [trader.ticker_id, str(stats['l']), str(stats['h'])]
    #    retstr = ','.join(jsstats)
    #    print(retstr)
    #    return retstr

    #@app.route('/get_klines_1hr')
    #def get_klines_1hr():
    #    klines = trader.accnt.get_klines(hours=4, ticker_id=trader.ticker_id)
    #    prices = []
    #    for kline in klines:
    #        prices.append(kline[4])
    #    return ','.join(prices)

    try:
        app.logger.setLevel(logging.ERROR)
        #app.logger.disabled = True
        #app.debug = False
        log = logging.getLogger('werkzeug')
        log.disabled = True
        app.run(host = '0.0.0.0',port=5000)
    except:
        sys.exit(0)
