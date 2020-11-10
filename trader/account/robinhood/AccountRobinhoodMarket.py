from trader.account.AccountBaseMarket import AccountBaseMarket
from trader.lib.struct.Exchange import Exchange

class AccountRobinhoodMarket(AccountBaseMarket):
    def __init__(self, client, info, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulate
        self.logger = logger
        self._tickers = {}
        self._min_tickers = {}
        self._max_tickers = {}

    def get_ticker(self, symbol=None):
        if not self.simulate:
            if not self.info.get_info_all_assets():
                self.info.load_exchange_info()
            sid = self.info.get_ticker_id(symbol)
            result = self.client.get_crypto_quote_from_id(id=sid)
            if result:
                try:
                    price = float(result['mark_price'])
                except KeyError:
                    price = 0.0
                return price
        try:
            price = self._tickers[symbol]
        except KeyError:
            price = 0.0
        return price

    def get_tickers(self):
        result = {}
        if not self.simulate:
            if not self.info.get_info_all_assets():
                self.info.load_exchange_info()
            for ticker in self.info.get_info_all_assets().keys():
                result[ticker] = self.get_ticker(ticker)
            return result
        else:
            result = self._tickers
        return result

    def get_ticker_symbols(self, currency=None):
        result = []
        mode = self.info.get_account_mode()
        if mode == Exchange.ACCOUNT_MODE_CRYPTO:
            if not self.info.get_info_all_assets():
                self.info.load_exchange_info()
            for ticker in self.info.get_info_all_assets().keys():
                result.append(ticker)
        elif mode == Exchange.ACCOUNT_MODE_STOCKS:
            # get list of watched stock symbols
            result = self.info.get_watched_symbols()
        return result

    def get_min_tickers(self):
        return self._min_tickers

    def get_max_tickers(self):
        return self._max_tickers

    def update_ticker(self, symbol, price, ts):
        if self.simulate:
            last_price = 0
            try:
                last_price = self._tickers[symbol]
            except KeyError:
                pass

            if not last_price:
                self._min_tickers[symbol] = [price, ts]
                self._max_tickers[symbol] = [price, ts]
            else:
                if price < self._min_tickers[symbol][0]:
                    self._min_tickers[symbol] = [price, ts]
                elif price > self._max_tickers[symbol][0]:
                    self._max_tickers[symbol] = [price, ts]

        self._tickers[symbol] = price

    def update_tickers(self, tickers):
        for symbol, price in tickers.items():
            self._tickers[symbol] = float(price)

    def get_klines(self, days=0, hours=1, mode='1D', ticker_id=None):
        klines = []

        if mode == 'LIVE':
            interval = '15second'
            span = 'hour'
        elif mode == '1D':
            interval = '5minute'
            span = 'day'
        elif mode == '1W':
            interval = 'hour'
            span = 'week'
        elif mode == '1M':
            interval = 'hour'
            span = 'month'
        elif mode == '3M':
            interval = 'day'
            span = '3month'
        elif mode == '1Y':
            interval = 'day'
            span = 'year'
        elif mode == '5Y':
            interval = 'week'
            span = '5year'
        else:
            if self.logger:
                self.logger.info("get_klines(): Invalid mode {}".format(mode))
            else:
                print("get_klines(): Invalid mode {}".format(mode))
            return klines

        id = self.info.get_ticker_id(ticker_id)
        result = self.client.get_crypto_historical_from_id(id, interval=interval, span=span, bound="24_7")
        for d in result['data_points']:
            ts = d['begins_at']
            l = d['low_price']
            h = d['high_price']
            o = d['open_price']
            c = d['close_price']
            v = d['volume']
            klines.append([ts, l, h, o, c, v])
        return klines

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        raise NotImplementedError