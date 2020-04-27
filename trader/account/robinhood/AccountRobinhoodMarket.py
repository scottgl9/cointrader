from trader.account.AccountBaseMarket import AccountBaseMarket

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
        if not self.info.get_info_all_assets():
            self.info.load_exchange_info()
        for ticker in self.info.get_info_all_assets().keys():
            result.append(ticker)
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

    # {'begins_at': '2020-04-24T13:40:00Z', 'open_price': '7498.020000', 'close_price': '7503.780000', 'high_price': '7522.225000', 'low_price': '7488.440000', 'volume': 0, 'session': 'reg', 'interpolated': False}
    def get_klines(self, days=0, hours=1, ticker_id=None):
        klines = []
        id = self.info.get_ticker_id(ticker_id)
        result = self.client.get_crypto_historical_from_id(id, interval="hour", span="month", bound="regular")
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