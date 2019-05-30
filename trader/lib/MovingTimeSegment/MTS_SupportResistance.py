from .MovingTimeSegment import MovingTimeSegment


class MTS_SRLine(object):
    SRTYPE_1HR = 1
    SRTYPE_12HR = 2
    SRTYPE_24HR = 3

    def __init__(self, type=1, s=0, r=0, start_ts=0, end_ts=0):
        self.type = type
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.s = s
        self.r = r
        self.ended = False

    def __str__(self):
        return str(self.__repr__())

    def __repr__(self):
        return str({'type': self.type,
                'start_ts': self.start_ts,
                'end_ts': self.end_ts,
                's': self.s,
                'r': self.r})


class MTS_SRInfo(object):
    def __init__(self, secs):
        self.secs = secs
        self.update_ts = 0
        self.prev_update_ts = 0
        self.support_update_ts = 0
        self.resistance_update_ts = 0
        self.prev_support_update_ts = 0
        self.prev_resistance_update_ts = 0
        self.support = 0
        self.resistance = 0
        self.started = False

    def reset(self):
        self.update_ts = 0
        self.reset_support()
        self.reset_resistance()

    def reset_support(self):
        self.support_update_ts = 0
        self.support = 0

    def reset_resistance(self):
        self.resistance_update_ts = 0
        self.resistance = 0


class MTS_SupportResistance(object):
    def __init__(self, percent_margin=0):
        self.percent_margin = percent_margin
        self.win_mts1 = 3600
        self.win_mts12 = 3600 * 12
        self.win_mts24 = 3600 * 24
        self.mts1 = MovingTimeSegment(seconds=self.win_mts1, disable_fmm=False)
        self.mts12 = MovingTimeSegment(seconds=self.win_mts12, disable_fmm=False)
        self.mts24 = MovingTimeSegment(seconds=self.win_mts24, disable_fmm=False)
        self.prev_mts1_info = None
        self.prev_mts12_info = None
        self.prev_mts24_info = None
        self.mts1_info = MTS_SRInfo(secs=self.mts1.seconds)
        self.mts12_info = MTS_SRInfo(secs=self.mts12.seconds)
        self.mts24_info = MTS_SRInfo(secs=self.mts24.seconds)
        self.srlines = []
        self.last_srlines_mts1_index = 0
        self.last_srlines_mts12_index = 0
        self.last_srlines_mts24_index = 0

    def find_support_resistance(self, mts, info, ts):
        # wait until mts.buffer is full
        if not mts.ready():
            return info

        if not info.support or not info.resistance:
            info.support = mts.min()
            info.prev_support_update_ts = info.support_update_ts
            info.prev_resistance_update_ts = info.resistance_update_ts
            info.support_update_ts = ts
            info.resistance = mts.max()
            info.resistance_update_ts = ts
            info.update_ts = ts
            info.started = True
        else:
            if mts.max() > info.resistance:
                info.resistance = mts.max()
                info.prev_resistance_update_ts = info.resistance_update_ts
                info.resistance_update_ts = ts
                info.last_update_ts = info.update_ts
                info.update_ts = ts
            if not info.support or mts.min() < info.support:
                info.support = mts.min()
                info.prev_support_update_ts = info.support_update_ts
                info.support_update_ts = ts
                info.last_update_ts = info.update_ts
                info.update_ts = ts
            if info.prev_support_update_ts - info.prev_resistance_update_ts >= info.secs * 1000:
                info.reset_resistance()
            elif info.prev_resistance_update_ts - info.prev_support_update_ts >= info.secs * 1000:
                info.reset_support()
            #if not info.counter and (info.support_counter >= info.window or info.resistance_counter >= info.window):
            #if info.support_counter - info.resistance_counter >= 0.5 * info.window:
            #    info.reset_resistance()
            #elif info.resistance_counter - info.support_counter >= 0.5 * info.window:
            #    info.reset_support()
        return info

    def update(self, value, ts):
        self.mts1.update(value, ts)
        self.mts12.update(value, ts)
        self.mts24.update(value, ts)

        if not self.mts1.ready():
            return False

        self.mts1_info = self.find_support_resistance(self.mts1, self.mts1_info, ts)

        if (ts - self.mts1_info.update_ts) > self.win_mts1 * 1000:
            if self.mts1_info.support_update_ts < self.mts1_info.resistance_update_ts:
                start_ts = self.mts1_info.support_update_ts
            else:
                start_ts = self.mts1_info.resistance_update_ts
            end_ts = ts
            srline = MTS_SRLine()
            srline.s = self.mts1_info.support
            srline.r = self.mts1_info.resistance
            if self.percent_margin:
                support_margin = float(100.0 - self.percent_margin) / 100.0
                resistance_margin = float(100.0 + self.percent_margin) / 100.0
                srline.s *= support_margin
                srline.r *= resistance_margin
            srline.start_ts = start_ts
            srline.end_ts = end_ts
            self.srlines.append(srline)
            self.mts1_info.reset()
            self.last_srlines_mts1_index = self.srlines.index(srline)

        if self.last_srlines_mts1_index and not self.srlines[self.last_srlines_mts1_index].ended:
            index = self.last_srlines_mts1_index
            if self.srlines[index].r >= value >= self.srlines[index].s:
                self.srlines[index].end_ts = ts
            else:
                self.srlines[index].ended = True

        if not self.mts12.ready():
            return False

        self.mts12_info = self.find_support_resistance(self.mts12, self.mts12_info, ts)

        if (ts - self.mts12_info.update_ts) > self.win_mts12 * 1000:
            if self.mts12_info.support_update_ts < self.mts12_info.resistance_update_ts:
                start_ts = self.mts12_info.support_update_ts
            else:
                start_ts = self.mts12_info.resistance_update_ts
            end_ts = ts
            srline = MTS_SRLine()
            srline.s = self.mts12_info.support
            srline.r = self.mts12_info.resistance
            if self.percent_margin:
                support_margin = float(100.0 - self.percent_margin) / 100.0
                resistance_margin = float(100.0 + self.percent_margin) / 100.0
                srline.s *= support_margin
                srline.r *= resistance_margin
            srline.start_ts = start_ts
            srline.end_ts = end_ts
            self.srlines.append(srline)
            self.mts12_info.reset()
            self.last_srlines_mts12_index = self.srlines.index(srline)

        if self.last_srlines_mts12_index and not self.srlines[self.last_srlines_mts12_index].ended:
            index = self.last_srlines_mts12_index
            if self.srlines[index].r >= value >= self.srlines[index].s:
                self.srlines[index].end_ts = ts
            else:
                self.srlines[index].ended = True

        if not self.mts24.ready():
            return False

        self.mts24_info = self.find_support_resistance(self.mts24, self.mts24_info, ts)

        if (ts - self.mts24_info.update_ts) > self.win_mts24 * 1000:
            # start_ts = kline.ts - 1000 * 3600 * self.win_weekly
            if self.mts24_info.support_update_ts < self.mts24_info.resistance_update_ts:
                start_ts = self.mts24_info.support_update_ts
            else:
                start_ts = self.mts24_info.resistance_update_ts
            end_ts = ts
            srline = MTS_SRLine()
            srline.s = self.mts24_info.support
            srline.r = self.mts24_info.resistance
            if self.percent_margin:
                support_margin = float(100.0 - self.percent_margin) / 100.0
                resistance_margin = float(100.0 + self.percent_margin) / 100.0
                srline.s *= support_margin
                srline.r *= resistance_margin
            srline.start_ts = start_ts
            srline.end_ts = end_ts
            self.srlines.append(srline)
            self.mts24_info.reset()
            self.last_srlines_mts24_index = self.srlines.index(srline)

        if self.last_srlines_mts24_index and not self.srlines[self.last_srlines_mts24_index].ended:
            index = self.last_srlines_mts24_index
            if self.srlines[index].r >= value >= self.srlines[index].s:
                self.srlines[index].end_ts = ts
            else:
                self.srlines[index].ended = True
