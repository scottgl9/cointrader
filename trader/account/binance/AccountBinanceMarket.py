from trader.account.CryptoAccountBaseMarket import CryptoAccountBaseMarket
from trader.account.binance.binance.client import Client


class AccountBinanceMarket(CryptoAccountBaseMarket):
    def __init__(self, client, info, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulate
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
            for ticker in self.client.get_all_tickers():
                result[ticker['symbol']] = ticker['price']
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
            result = self.info.get_info_all_pairs().keys()
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

    def get_klines(self, days=0, hours=1, mode=None, ticker_id=None):
        timestr = ''
        if days == 1:
            timestr = "1 day ago"
        elif days > 1:
            timestr = "{} days ago".format(days)
        if days == 0:
            if hours == 1:
                timestr = "1 hour ago"
            elif hours > 1:
                timestr = "{} hours ago".format(hours)
        else:
            if hours == 1:
                timestr = "and 1 hour ago"
            elif hours > 1:
                timestr = "and {} hours ago".format(hours)
        timestr += " UTC"

        klines_data = self.client.get_historical_klines(ticker_id, Client.KLINE_INTERVAL_1MINUTE, timestr)

        # reorganize kline format to same as GDAX for consistency:
        # GDAX kline format: [ timestamp, low, high, open, close, volume ]
        # binance format: [opentime, open, high, low, close, volume, closetime quotevolume, tradecount,
        # taker_buy_base_volume, taker_buy_currency_volume, ignore]
        klines = []
        for k in klines_data:
            ts = k[0] / 1000
            klines.append([ts, k[3], k[2], k[1], k[4], k[5]])

        return klines

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        result = []
        klines = self.client.get_historical_klines_generator(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            start_str=start_ts,
            end_str=end_ts,
        )
        # ['ts', 'open', 'high', 'low', 'close', 'quote_volume']
        for k in klines:
            result.append([k[0], k[1], k[2], k[3], k[4], k[6]])

        return result
