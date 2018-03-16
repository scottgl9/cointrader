from datetime import timedelta, datetime
from trader import gdax


class Volatility:
    def __init__(self, ticker_id):
        self.klines = None
        self.ticker_id = ticker_id
        self.pc = gdax.PublicClient()
        stats = self.pc.get_product_24hr_stats(self.ticker_id)
        self.high_24hr = float(stats['high'])
        self.low_24hr = float(stats['low'])
        self.open_24hr = float(stats['open'])
        self.mid_24hr = (self.low_24hr + self.high_24hr) / 2.0
        self.refresh()

    def refresh(self):
        self.klines = self.get_klines_hours(24)

    def get_klines_hours(self, hours=1):
        end = datetime.utcnow()
        start = (end - timedelta(hours=hours))
        return self.pc.get_product_historic_rates(self.ticker_id, start.isoformat(), end.isoformat(), 5*60)

    def count_frames_direction_from_klines(self):
        upcnt = 0
        downcnt = 0
        upchange = 0.0
        downchange = 0.0
        cross_up_count = 0
        cross_down_count = 0

        for kline in self.klines:
            openprice = float(kline[3])
            closeprice = float(kline[4])
            if closeprice > openprice:
                upcnt += 1
                upchange += closeprice - openprice
                if openprice < self.mid_24hr and closeprice > self.mid_24hr:
                    cross_up_count += 1
            elif closeprice < openprice:
                downcnt += 1
                downchange += openprice - closeprice
                if openprice > self.mid_24hr and closeprice < self.mid_24hr:
                    cross_down_count += 1

        return upchange, downchange, cross_up_count, cross_down_count

    def info(self):
        upchange, downchange, upcount, downcount = self.count_frames_direction_from_klines()
        print("low:{} high:{} upchange: {} downchange: {} upcount: {} downcount: {}".format(self.low_24hr, self.high_24hr, upchange, downchange, upcount, downcount))