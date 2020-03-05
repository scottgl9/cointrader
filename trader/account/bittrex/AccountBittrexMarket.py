from trader.account.AccountBaseMarket import AccountBaseMarket

class AccountBittrexMarket(AccountBaseMarket):
    def __init__(self, client, info, simulation=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulation
        self.logger = logger
        self._tickers = {}
        self._min_tickers = {}
        self._max_tickers = {}

    def get_ticker(self, symbol):
        if not self.simulate and len(self._tickers) == 0:
            self._tickers = self.get_tickers()
        try:
            price = self._tickers[symbol]
        except KeyError:
            price = 0.0
        return price

    def get_tickers(self):
        result = {}
        if not self.simulate:
            info_tickers = self.client.get_market_summaries()
            if not info_tickers['success']:
                return result
            for info in info_tickers['result']:
                #market_info = info['Market']
                market_summary = info['Summary']
                ticker_id = market_summary['MarketName']
                price = market_summary['Last']
                result[ticker_id] = price
        else:
            result = self._tickers
        return result

    def get_ticker_symbols(self, currency=None):
        result = []
        if not self.simulate:
            for ticker in self.client.get_all_tickers():
                if currency and ticker['symbol'].endswith(currency):
                    result.append(ticker['symbol'])
                elif not currency:
                    result.append(ticker['symbol'])
        else:
            result = self.info.get_info_all_assets().keys()
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

    def get_klines(self, days=0, hours=1, ticker_id=None):
        raise NotImplementedError

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        raise NotImplementedError
