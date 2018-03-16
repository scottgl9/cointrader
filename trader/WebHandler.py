#!/usr/bin/python
from flask import Flask, render_template, json, request,redirect,session,jsonify
from flask.logging import *
import threading
import sys
import json
import logging

app = Flask(__name__)
#app.logger.removeHandler(app.logger.disabled)
def WebThread(trader):
    if not trader:
        print("Failed to load trader")
        sys.exit(-1)
    print(trader.accnt.quote_currency_available)

    @app.route('/')
    def index():
        return render_template('prices.html')

    @app.route('/basic')
    def basic():
        return render_template('basic.html')

    @app.route('/update_stats')
    def update_stats():
        page = str('')
        page += trader.html_run_stats()
        page += trader.accnt.html_run_stats()
        page += trader.order_handler.html_run_stats()
        return page

    @app.route('/update_prices')
    def update_prices():
        #if trader.last_50_prices == trader.prev_last_50_prices:
        #    return ''
        trader.prev_last_50_prices = trader.last_50_prices
        return str(trader.last_50_prices)[1:-1]

    try:
        app.logger.setLevel(logging.ERROR)
        app.logger.disabled = True
        app.debug = False
        log = logging.getLogger('werkzeug')
        log.disabled = True
        app.run(host = '0.0.0.0',port=5000)
    except:
        sys.exit(0)