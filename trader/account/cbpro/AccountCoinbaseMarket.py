from trader.account.AccountBaseMarket import AccountBaseMarket
from .cbpro import AuthenticatedClient, PublicClient
from datetime import datetime, timedelta
import time
import aniso8601
import stix.utils.dates

class AccountCoinbaseMarket(AccountBaseMarket):
    def __init__(self, client, info, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulate
        self.logger = logger
        self._tickers = {}
        self._min_tickers = {}
        self._max_tickers = {}
        self.pc = PublicClient()

    def ts_to_iso8601(self, ts):
        dt = datetime.fromtimestamp(ts)
        return stix.utils.dates.serialize_value(dt)

    def get_ticker(self, symbol=None):
        if not self.simulate:
            if symbol:
                result = self.client.get_product_ticker(product_id=symbol)
                if result:
                    try:
                        price = float(result['price'])
                    except KeyError:
                        price = 0.0
                    return price
            #elif not len(self._tickers):
            #    self._tickers = self.get_all_tickers()
        try:
            price = self._tickers[symbol]
        except KeyError:
            price = 0.0
        return price

    def get_tickers(self):
        return self._tickers

    def get_ticker_symbols(self, currency=None):
        result = []
        if not self.simulate:
            products = self.pc.get_products()
            for product in products:
                if currency and product['id'].endswith(currency):
                    result.append(product['id'])
                else:
                    result.append(product['id'])
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

    # The granularity field must be one of the following values: {60, 300, 900, 3600, 21600, 86400}
    # The maximum amount of data returned is 300 candles
    # kline format: [ timestamp, low, high, open, close, volume ]
    def get_klines(self, days=0, hours=1, ticker_id=None):
        end = datetime.utcnow()
        start = (end - timedelta(days=days, hours=hours))
        granularity = 900
        if days == 0 and hours < 6:
            granularity = 60
        elif (days== 0 and hours <= 24) or (days == 1 and hours == 0):
            granularity = 300

        rates = self.pc.get_product_historic_rates(ticker_id,
                                                   start.isoformat(),
                                                   end.isoformat(),
                                                   granularity=granularity)
        return rates[::-1]


    def get_hourly_klines(self, symbol, start_ts, end_ts, reverse=False):
        result = []
        if not reverse:
            ts1 = start_ts
            ts2 = end_ts
            while ts1 <= end_ts:
                ts2 = end_ts
                if (ts2 - ts1) > 3600 * 250:
                    ts2 = ts1 + 3600 * 250
                start = self.ts_to_iso8601(ts1)
                end = self.ts_to_iso8601(ts2)

                klines = self.pc.get_product_historic_rates(product_id=symbol,
                                                            start=start,
                                                            end=end,
                                                            granularity=3600)
                ts1 = ts2 + 3600
                if isinstance(klines, list):
                    try:
                        if len(klines):
                            result += reversed(klines)
                    except TypeError:
                        print(klines, type(klines))
                        pass
                    time.sleep(1)
                else:
                    if klines['message'] == 'NotFound':
                        time.sleep(1)
                        continue
                    print("ERROR get_hourly_klines(): {}".format(klines['message']))
                    return result
        # else:
        #     ts1 = start_ts
        #     ts2 = end_ts
        #     while ts1 >= start_ts:
        #         ts1 = start_ts
        #         if (ts2 - ts1) > 3600 * 250:
        #             ts1 = ts2 - 3600 * 250
        #         start = self.ts_to_iso8601(ts1)
        #         end = self.ts_to_iso8601(ts2)
        #         klines = self.pc.get_product_historic_rates(product_id=symbol,
        #                                                     start=start,
        #                                                     end=end,
        #                                                     granularity=3600)
        #         ts1 = ts2 - 3600
        #         if isinstance(klines, list):
        #             try:
        #                 result = reversed(klines) + result
        #             except TypeError:
        #                 pass
        #             time.sleep(1)
        #         else:
        #             if klines['message'] == 'NotFound':
        #                 break
        #             print("ERROR get_hourly_klines(): {}".format(klines['message']))
        #             return result

        return result
