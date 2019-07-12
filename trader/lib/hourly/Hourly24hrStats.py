# track 24 hour stats from hourly kline data such as 24hr base_volume and 24hr quote_volume


class Hourly24hrStats(object):
    def __init__(self, symbol=None, accnt=None, hkdb=None):
        self.symbol = symbol
        self.accnt = accnt
        self.hkdb = hkdb
        self.pre_load_hours = 24
        self.klines = []
        self.klines_loaded = False
        self.first_hourly_ts = 0
        self.last_hourly_ts = 0
        self.last_update_ts = 0
        self._base_volume_sum = 0
        self._quote_volume_sum = 0

    def ready(self):
        return self.klines_loaded

    def hourly_load(self, hourly_ts=0, pre_load_hours=0, ts=0):
        end_ts = hourly_ts
        start_ts = end_ts - self.accnt.hours_to_ts(self.pre_load_hours - 1)
        klines = self.hkdb.get_dict_klines(self.symbol, start_ts=start_ts, end_ts=end_ts)
        if len(klines) < self.pre_load_hours:
            return
        for kline in klines:
            self._base_volume_sum += float(kline['base_volume'])
            self._quote_volume_sum += float(kline['quote_volume'])
        self.klines = klines
        self.klines_loaded = True

    def hourly_update(self, hourly_ts):
        #if not self.klines:
        #    return False

        kline = self.hkdb.get_dict_kline(self.symbol, hourly_ts)

        # hourly kline not in db yet, wait until next update() call
        if not kline:
            return False

        if self.klines_loaded:
            self._base_volume_sum -= float(self.klines[0]['base_volume'])
            self._quote_volume_sum -= float(self.klines[0]['quote_volume'])
            # remove oldest kline, and add new kline to end
            self.klines = self.klines[1:]

        self.klines.append(kline)
        self._base_volume_sum += float(kline['base_volume'])
        self._quote_volume_sum += float(kline['quote_volume'])

        if not self.klines_loaded and len(self.klines) >= self.pre_load_hours:
            self.klines_loaded = True

        self.last_hourly_ts = hourly_ts
        return True

    def get_base_volume_24hr(self):
        if len(self.klines) < self.pre_load_hours:
            return 0
        return self._base_volume_sum / float(self.pre_load_hours)


    def get_quote_volume_24hr(self):
        if len(self.klines) < self.pre_load_hours:
            return 0
        return self._quote_volume_sum / float(self.pre_load_hours)
