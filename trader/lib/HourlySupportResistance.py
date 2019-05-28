# use hourly klines from hourly klines DB to analyze support/resistance lines
# hourly klines will be used to generate the following information:
# 1) major and minor support/resistance lines in the daily (24hr) timeframe
# 2) major and minor support/resistance lines in the weekly (168hr) timeframe
# 3)  major and minor support/resistance lines in the monthly (730hr) timeframe

# DESIGN:
# track close prices for daily, weekly, and monthly
# 1) if for the specified timeframe, close prices do not exceed a given high when backtesting current high,
# then set high as new resistance line
# 2) if for the specified timeframe, close prices do not drop below a given low when backtesting current low,
# then set low as new support line
# 3) With established support / resistance lines. If the price has dropped below the support line for amount of time
# of specified timeframe, then support line converted to resistance line, and again do step #2 to get new support
# 4) With established support / resistance lines. If the price has exceeded above the resistance line for amount of time
# of specified timeframe, then resistance line converted to support line, and again do step #1 to get new support

from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.lib.struct.CircularArray import CircularArray


class HourlySRLine(object):
    SRTYPE_DAILY = 1
    SRTYPE_WEEKLY = 2
    SRTYPE_MONTHLY = 3

    def __init__(self, type, s, r, start_ts=0, end_ts=0):
        self.type = type
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.s = s
        self.r = r

    def __str__(self):
        return str(self.__repr__())

    def __repr__(self):
        return str({'type': self.type,
                'start_ts': self.start_ts,
                'end_ts': self.end_ts,
                's': self.s,
                'r': self.r})


class SRInfo(object):
    def __init__(self, window):
        self.window=window
        self.counter = 0
        self.support_counter = 0
        self.resistance_counter = 0
        self.support_update_ts = 0
        self.resistance_update_ts = 0
        self.prev_support_update_ts = 0
        self.prev_resistance_update_ts = 0
        self.support = 0
        self.resistance = 0
        self.started = False

    def reset(self):
        self.counter = 0
        self.reset_support()
        self.reset_resistance()

    def reset_support(self):
        self.support_counter = 0
        self.support_update_ts = 0
        self.support = 0

    def reset_resistance(self):
        self.resistance_counter = 0
        self.resistance_update_ts = 0
        self.resistance = 0


class HourlySupportResistance(object):
    def __init__(self, symbol, accnt=None, filename=None, db=None):
        self.accnt = accnt
        self.filename = filename
        self.symbol = symbol
        self.db = db
        if not self.db:
            self.db = HourlyKlinesDB(self.accnt, self.filename, self.symbol)
        self.win_daily = 24
        self.win_weekly = 168
        self.win_monthly = 730
        self.daily_closes = CircularArray(window=self.win_daily)
        # self.daily_lows = CircularArray(window=self.win_daily)
        # self.daily_highs = CircularArray(window=self.win_daily)
        self.weekly_closes = CircularArray(window=self.win_weekly)
        # self.weekly_lows = CircularArray(window=self.win_weekly)
        # self.weekly_highs = CircularArray(window=self.win_weekly)
        self.monthly_closes = CircularArray(window=self.win_monthly)
        # self.monthly_lows = CircularArray(window=self.win_monthly)
        # self.monthly_highs = CircularArray(window=self.win_monthly)
        self.srlines = []
        self.start_ts = 0
        self.daily_info = SRInfo(self.win_daily)
        self.weekly_info = SRInfo(self.win_weekly)
        self.monthly_info = SRInfo(self.win_monthly)
        self.prev_daily_info = SRInfo(self.win_daily)
        self.prev_weekly_info = SRInfo(self.win_weekly)
        self.prev_monthly_info = SRInfo(self.win_monthly)
        self.daily_support = 0
        self.daily_resistance = 0
        self.weekly_support = 0
        self.weekly_resistance = 0
        self.monthly_support = 0
        self.monthly_resistance = 0


    def load(self, hourly_start_ts=0, hourly_end_ts=0, klines=None):
        if not klines:
            klines = self.db.get_klines(self.symbol, hourly_start_ts, hourly_end_ts)

        if len(klines):
            self.start_ts = klines[0].ts

        for kline in klines:
            self.daily_closes.add(kline.close)
            self.weekly_closes.add(kline.close)
            self.monthly_closes.add(kline.close)


    def find_support_resistance(self, kline, closes, info):
        # wait until closes buffer is full
        if not closes.full():
            return info

        if not info.support or not info.resistance:
            if not info.started:
                info.support = closes.min()
            else:
                info.support = kline.low
            info.prev_support_update_ts = info.support_update_ts
            info.prev_resistance_update_ts = info.resistance_update_ts
            info.support_update_ts = kline.ts
            if not info.started:
                info.resistance = closes.max()
            else:
                info.resistance = kline.high
            info.resistance_update_ts = kline.ts
            info.counter = 0
            info.started = True
        else:
            info.support_counter += 1
            info.resistance_counter += 1
            info.counter += 1
            if kline.high > info.resistance:
                info.resistance = kline.high
                info.prev_resistance_update_ts = info.resistance_update_ts
                info.resistance_update_ts = kline.ts
                info.resistance_counter = 0
                info.counter = 0
            if not info.support or kline.low < info.support:
                info.support = kline.low
                info.prev_support_update_ts = info.support_update_ts
                info.support_update_ts = kline.ts
                info.support_counter = 0
                info.counter = 0
            #if not info.counter and (info.support_counter >= info.window or info.resistance_counter >= info.window):
            if info.support_counter - info.resistance_counter >= 0.5 * info.window:

                info.reset_resistance()
            elif info.resistance_counter - info.support_counter >= 0.5 * info.window:
                info.reset_support()
            #if info.prev_support_update_ts and info.support_update_ts and (info.support_update_ts - info.prev_support_update_ts) > 0.1 * 1000 * 3600 * info.window:
            #    #info.prev_support_update_ts = info.support_update_ts
            #    info.reset_support()
            #if info.prev_resistance_update_ts and info.resistance_update_ts and (info.resistance_update_ts - info.prev_resistance_update_ts) > 0.1 * 1000 * 3600 * info.window:
            #    #info.prev_resistance_update_ts = info.resistance_update_ts
            #    info.reset_resistance()
        return info

    def update(self, hourly_ts=0, kline=None):
        if not kline:
            kline = self.db.get_kline(self.symbol, hourly_ts)

        if not self.start_ts:
            self.start_ts = kline.ts

        self.daily_closes.add(kline.close)
        self.weekly_closes.add(kline.close)
        self.monthly_closes.add(kline.close)

        if len(self.daily_closes) < self.win_daily:
            return

        self.daily_info = self.find_support_resistance(kline, self.daily_closes, self.daily_info)

        if self.daily_info.counter > self.win_daily:
            # start_ts = kline.ts - 1000 * 3600 * self.win_daily
            if self.weekly_info.support_update_ts < self.weekly_info.resistance_update_ts:
                start_ts = self.daily_info.support_update_ts
            else:
                start_ts = self.daily_info.resistance_update_ts
            end_ts = kline.ts
            self.daily_support = self.daily_info.support
            self.daily_resistance = self.daily_info.resistance
            self.daily_info.counter = 0
            self.daily_info.support_update_ts = 0
            self.daily_info.resistance_update_ts = 0
            self.daily_info.support_counter = 0
            self.daily_info.resistance_counter = 0
            self.prev_daily_info = self.daily_info
            self.daily_info.support = 0
            self.daily_info.resistance = 0

            srline = HourlySRLine(HourlySRLine.SRTYPE_DAILY, self.daily_support, self.daily_resistance, start_ts, end_ts)
            self.srlines.append(srline)

        if len(self.weekly_closes) < self.win_weekly:
            return

        self.weekly_info = self.find_support_resistance(kline, self.weekly_closes, self.weekly_info)

        if self.weekly_info.counter > self.win_weekly:
            # start_ts = kline.ts - 1000 * 3600 * self.win_weekly
            if self.weekly_info.support_update_ts < self.weekly_info.resistance_update_ts:
                start_ts = self.weekly_info.support_update_ts
            else:
                start_ts = self.weekly_info.resistance_update_ts
            end_ts = kline.ts
            self.weekly_support = self.weekly_info.support
            self.weekly_resistance = self.weekly_info.resistance
            self.weekly_info.counter = 0
            self.weekly_info.support_update_ts = 0
            self.weekly_info.resistance_update_ts = 0
            self.weekly_info.support_counter = 0
            self.weekly_info.resistance_counter = 0
            self.prev_weekly_info = self.weekly_info
            self.weekly_info.support = 0
            self.weekly_info.resistance = 0

            srline = HourlySRLine(HourlySRLine.SRTYPE_WEEKLY, self.weekly_support, self.weekly_resistance,
                                  start_ts, end_ts)
            self.srlines.append(srline)

        if len(self.monthly_closes) < self.win_monthly:
            return

        self.monthly_info = self.find_support_resistance(kline, self.monthly_closes, self.monthly_info)

        if self.monthly_info.counter > self.win_monthly:
            #start_ts = kline.ts - 1000 * 3600 * self.win_monthly
            if self.monthly_info.support_update_ts < self.monthly_info.resistance_update_ts:
                start_ts = self.monthly_info.support_update_ts
            else:
                start_ts = self.monthly_info.resistance_update_ts
            end_ts = kline.ts
            self.monthly_support = self.monthly_info.support
            self.monthly_resistance = self.monthly_info.resistance
            self.monthly_info.counter = 0
            self.monthly_info.support_update_ts = 0
            self.monthly_info.resistance_update_ts = 0
            self.monthly_info.support_counter = 0
            self.monthly_info.resistance_counter = 0
            self.prev_monthly_info = self.monthly_info
            self.monthly_info.support = 0
            self.monthly_info.resistance = 0

            srline = HourlySRLine(HourlySRLine.SRTYPE_MONTHLY, self.monthly_support, self.monthly_resistance,
                                  start_ts, end_ts)
            self.srlines.append(srline)
