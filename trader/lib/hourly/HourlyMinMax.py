#                                         192 hourly min max
#+---------------+---------------------------------------------------------------------------+
#|               |              cur 96 hr                                                    |
#|               +---------------+-----------------------------------------------------------+
#|               |               |            cur 48hr                                       |
#|               |               +-------------+---------------------------------------------+
#|               |               |             |            cur 24hr                         |
#|               |               |             +----------------+----------------------------+
#|               |               |             |                |             cur 12hr       |
#|               |               |             |                +-------------+--------------+
#|  prev 96hr    |  prev 48hr    |  prev 24hr  |  prev 12hr     |  prev 8hr   |              |
#|               |               |             |                +-------------+    cur 4hr   |
#|               |               |             |                |  | prev 4hr |              |
#+---------------+---------------+-------------+----------------+-------------+--------------+

class HourlyMinMax(object):
    def __init__(self, symbol=None, accnt=None, hkdb=None):
        self.symbol = symbol
        self.accnt = accnt
        self.hkdb = hkdb
        self.pre_load_hours = 192

        # hourly vars
        self.hourly_highs = []
        self.hourly_lows = []
        self.first_hourly_ts = 0
        self.last_hourly_ts = 0
        self.last_update_ts = 0
        self.klines = None
        self.prev_96hr_low = 0
        self.prev_96hr_high = 0
        self.cur_96hr_low = 0
        self.cur_96hr_high = 0
        self.prev_48hr_low = 0
        self.prev_48hr_high = 0
        self.cur_48hr_low = 0
        self.cur_48hr_high = 0
        self.prev_24hr_low = 0
        self.prev_24hr_high = 0
        self.cur_24hr_low = 0
        self.cur_24hr_high = 0
        self.prev_12hr_low = 0
        self.prev_12hr_high = 0
        self.cur_12hr_low = 0
        self.cur_12hr_high = 0
        self.prev_8hr_low = 0
        self.prev_8hr_high = 0
        self.cur_4hr_low = 0
        self.cur_4hr_high = 0

    def hourly_load(self, hourly_ts=0, pre_load_hours=0, ts=0):
        end_ts = hourly_ts
        start_ts = end_ts - self.accnt.hours_to_ts(self.pre_load_hours - 1)
        klines = self.hkdb.get_dict_klines(self.symbol, start_ts=start_ts, end_ts=end_ts)
        if len(klines) < self.pre_load_hours:
            return
        self.klines = klines
        for kline in self.klines:
            low = float(kline['low'])
            high = float(kline['high'])
            self.hourly_lows.append(low)
            self.hourly_highs.append(high)
        self.compute_hourly_lows_highs()
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        self.last_hourly_ts = self.first_hourly_ts

    def hourly_update(self, hourly_ts):
        if not self.klines:
            return

        kline = self.hkdb.get_dict_kline(self.symbol, hourly_ts)

        # hourly kline not in db yet, wait until next update() call
        if not kline:
            return False

        self.hourly_lows = self.hourly_lows[1:]
        self.hourly_highs = self.hourly_highs[1:]
        self.hourly_lows.append(float(kline['low']))
        self.hourly_highs.append(float(kline['high']))

        # remove oldest kline, and add new kline to end
        self.klines = self.klines[1:]
        self.klines.append(kline)

        self.compute_hourly_lows_highs()

        self.last_hourly_ts = hourly_ts
        return False


    def compute_hourly_lows_highs(self):
        self.prev_96hr_low = 0
        self.prev_96hr_high = 0
        self.prev_48hr_low = 0
        self.prev_48hr_high = 0
        self.prev_24hr_low = 0
        self.prev_24hr_high = 0
        self.prev_12hr_low = 0
        self.prev_12hr_high = 0
        self.cur_96hr_low = 0
        self.cur_96hr_high = 0
        self.cur_48hr_low = 0
        self.cur_48hr_high = 0
        self.cur_24hr_low = 0
        self.cur_24hr_high = 0
        self.cur_12hr_low = 0
        self.cur_12hr_high = 0
        self.prev_8hr_low = 0
        self.prev_8hr_high = 0
        self.prev_4hr_low = 0
        self.prev_4hr_high = 0
        self.cur_4hr_low = 0
        self.cur_4hr_high = 0

        for i in range(0, 96):
            if not self.prev_96hr_low or self.hourly_lows[i] < self.prev_96hr_low:
                self.prev_96hr_low = self.hourly_lows[i]
            if self.hourly_highs[i] > self.prev_96hr_high:
                self.prev_96hr_high = self.hourly_highs[i]
        for i in range(96, 192):
            if not self.cur_96hr_low or self.hourly_lows[i] < self.cur_96hr_low:
                self.cur_96hr_low = self.hourly_lows[i]
            if self.hourly_highs[i] > self.cur_96hr_high:
                self.cur_96hr_high = self.hourly_highs[i]

            j = i - 96

            # update prev and cur 48hr lows and highs
            if j < 48:
                if not self.prev_48hr_low or self.hourly_lows[i] < self.prev_48hr_low:
                    self.prev_48hr_low = self.hourly_lows[i]
                if self.hourly_highs[i] > self.prev_48hr_high:
                    self.prev_48hr_high = self.hourly_highs[i]
            else:
                if not self.cur_48hr_low or self.hourly_lows[i] < self.cur_48hr_low:
                    self.cur_48hr_low = self.hourly_lows[i]
                if self.hourly_highs[i] > self.cur_48hr_high:
                    self.cur_48hr_high = self.hourly_highs[i]

            j -= 48
            # update prev and cur 24hr lows and highs
            if j >= 0:
                if j < 24:
                    if not self.prev_24hr_low or self.hourly_lows[i] < self.prev_24hr_low:
                        self.prev_24hr_low = self.hourly_lows[i]
                    if self.hourly_highs[i] > self.prev_24hr_high:
                        self.prev_24hr_high = self.hourly_highs[i]
                else:
                    if not self.cur_24hr_low or self.hourly_lows[i] < self.cur_24hr_low:
                        self.cur_24hr_low = self.hourly_lows[i]
                    if self.hourly_highs[i] > self.cur_24hr_high:
                        self.cur_24hr_high = self.hourly_highs[i]

            j -= 24
            # update prev and cur 12hr lows and highs
            if j >= 0:
                if j < 12:
                    if not self.prev_12hr_low or self.hourly_lows[i] < self.prev_12hr_low:
                        self.prev_12hr_low = self.hourly_lows[i]
                    if self.hourly_highs[i] > self.prev_12hr_high:
                        self.prev_12hr_high = self.hourly_highs[i]
                else:
                    if not self.cur_12hr_low or self.hourly_lows[i] < self.cur_12hr_low:
                        self.cur_12hr_low = self.hourly_lows[i]
                    if self.hourly_highs[i] > self.cur_12hr_high:
                        self.cur_12hr_high = self.hourly_highs[i]

            j -= 12

            if j >= 0:
                if j < 8:
                    if j >= 4:
                        if not self.prev_4hr_low or self.hourly_lows[i] < self.prev_4hr_low:
                            self.prev_4hr_low = self.hourly_lows[i]
                        if self.hourly_highs[i] > self.prev_4hr_high:
                            self.prev_4hr_high = self.hourly_highs[i]
                    if not self.prev_8hr_low or self.hourly_lows[i] < self.prev_8hr_low:
                        self.prev_8hr_low = self.hourly_lows[i]
                    if self.hourly_highs[i] > self.prev_8hr_high:
                        self.prev_8hr_high = self.hourly_highs[i]
                else:
                    if not self.cur_4hr_low or self.hourly_lows[i] < self.cur_4hr_low:
                        self.cur_4hr_low = self.hourly_lows[i]
                    if self.hourly_highs[i] > self.cur_4hr_high:
                        self.cur_4hr_high = self.hourly_highs[i]
