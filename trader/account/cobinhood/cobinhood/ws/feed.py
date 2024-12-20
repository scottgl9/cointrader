import logging
import traceback
import time
import json
import threading
import websocket
import coloredlogs
from trader.account.cobinhood.cobinhood.configuration import Config
from trader.account.cobinhood.cobinhood.ws.response import ExchangeData

logging.basicConfig()
logger = logging.getLogger('cobinhood.ws')


class CobinhoodWS(object):
    def __init__(self):
        coloredlogs.install(level=Config.LOG_LEVEL, logger=logger)
        self.pingThread = threading.Thread(target=self.ping)
        self.pingThread.setDaemon(True)
        self._subscribe = []
        self.ws = None
        self.msg_callback = None
        self.exchange_data = ExchangeData()

    def start(self, subscribe=None, on_message=None):
        if on_message:
            self.msg_callback = on_message
        if subscribe:
            self._subscribe = subscribe
        if Config.API_TOKEN:
            headers = 'Authorization: %s' % Config.API_TOKEN
            self.ws = websocket.WebSocketApp(Config.WS_URL,
                                             on_open=self.on_open,
                                             on_close=self.on_close,
                                             on_error=self.on_error,
                                             on_message=self.on_message,
                                             header=[headers])
        else:
            self.ws = websocket.WebSocketApp(Config.WS_URL,
                                             on_open=self.on_open,
                                             on_close=self.on_close,
                                             on_message=on_message)
        while True:
            self.ws.run_forever()
            time.sleep(3)

    def ping(self):
        while True:
            self.post_message('{"action": "ping"}')
            time.sleep(30)

    def on_error(self, unused_ws, error):
        logger.error('WS Error: %s', error)

    def on_open(self, unused_ws):
        logger.info('Websocket Connected!')
        for topic in self._subscribe:
            self.post_message(str(topic))
        if not self.pingThread.ident:
            self.pingThread.start()

    def on_close(self, unused_ws):
        logger.info('Websocket Closed!')

    def on_message(self, unused_ws, msg):
        try:
            logger.debug(msg)
            msg = json.loads(msg)
            if 'channel_id' in msg.keys():
                if 'event' in msg.keys():
                    event = msg['event']
                elif 'update' in msg.keys():
                    event = 'update'
                elif 'snapshot' in msg.keys():
                    event = 'snapshot'
                else:
                    event = ''
                logger.info('Receive: %s %s', event, msg['channel_id'])
            if 'action' not in msg.keys() and 'event' not in msg.keys():
                self.exchange_data.dispatcher(msg)
            if self.msg_callback:
                self.msg_callback(self, msg)
        except Exception as e:
            logger.error('%s, %s', msg, e)
            logger.error(traceback.print_exc())

    def post_message(self, msg):
        logger.info('Send %s', msg)
        self.ws.send(msg)
