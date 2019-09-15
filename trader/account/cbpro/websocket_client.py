# cbpro/WebsocketClient.py
# original author: Daniel Paquin
# mongo "support" added by Drew Rice
#
#
# Template object to receive messages from the Coinbase Websocket Feed

from __future__ import print_function
import json
import base64
import hmac
import hashlib
import time
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException
from pymongo import MongoClient
from .cbpro_auth import get_auth_headers


class WebsocketClient(object):
    def __init__(self, url="wss://ws-feed.pro.coinbase.com", products=None, message_type="subscribe", db=None,
                 should_print=True, auth=False, api_key="", api_secret="", api_passphrase="", channels=None):
        self.url = url
        self.products = products
        self.channels = channels
        self.type = message_type
        self.stop = True
        self.error = None
        self.ws = None
        self.thread = None
        self.auth = auth
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.should_print = should_print
        self.db = db

    def start(self):
        def _go():
            self._connect()
            self._listen()
            self._disconnect()

        self.stop = False
        self.on_open()
        self.thread = Thread(target=_go)
        self.keepalive = Thread(target=self._keepalive)
        self.thread.start()

    def _connect(self):
        if self.products is None:
            self.products = ["BTC-USD"]
        elif not isinstance(self.products, list):
            self.products = [self.products]

        if self.url[-1] == "/":
            self.url = self.url[:-1]

        if self.channels is None:
            sub_params = {'type': 'subscribe', 'product_ids': self.products}
        else:
            sub_params = {'type': 'subscribe', 'product_ids': self.products, 'channels': self.channels}

        if self.auth:
            timestamp = str(time.time())
            message = timestamp + 'GET' + '/users/self/verify'
            auth_headers = get_auth_headers(timestamp, message, self.api_key, self.api_secret, self.api_passphrase)
            sub_params['signature'] = auth_headers['CB-ACCESS-SIGN']
            sub_params['key'] = auth_headers['CB-ACCESS-KEY']
            sub_params['passphrase'] = auth_headers['CB-ACCESS-PASSPHRASE']
            sub_params['timestamp'] = auth_headers['CB-ACCESS-TIMESTAMP']

        self.ws = create_connection(self.url)

        self.ws.send(json.dumps(sub_params))

    def _keepalive(self, interval=30):
        while not self.stop and self.ws and self.ws.connected:
            self.ws.ping("keepalive")
            time.sleep(interval)

    def _listen(self):
        data = None
        self.keepalive.start()
        while not self.stop and self.ws and self.ws.connected:
            try:
                data = self.ws.recv()
            except (KeyboardInterrupt, SystemExit):
                self.stop = True
                break
            if not data:
                self.stop = True
                break
            try:
                msg = json.loads(data)
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
            else:
                self.on_message(msg)
        print("Shutting down...")
        self.close()

    def _disconnect(self):
        try:
            if self.ws:
                self.ws.close()
                self.ws = None
        except WebSocketConnectionClosedException as e:
            pass
        finally:
            self.keepalive.join()

        self.on_close()

    def close(self):
        if self.db:
            self.db.commit()
            self.db.close()
            self.db = None
        self.stop = True   # will only disconnect after next msg recv
        self._disconnect() # force disconnect so threads can join
        self.thread.join()

    def on_open(self):
        if self.should_print:
            print("-- Subscribed! --\n")

    def on_close(self):
        if self.should_print:
            print("\n-- Socket Closed --")

    def on_message(self, msg):
        if self.should_print:
            print(msg)

    def on_error(self, e, data=None):
        self.error = e
        self.stop = True
        print('{} - data: {}'.format(e, data))