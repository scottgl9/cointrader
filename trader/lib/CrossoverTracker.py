from trader.lib.MovingTimeSegment.MTSCrossover2 import MTSCrossover2
from trader.lib.Crossover2 import Crossover2


class CrossoverTracker(object):
    def __init__(self, window=0, win_secs=0, hourly_mode=False):
        self.hourly_mode = hourly_mode
        self.win_secs = win_secs
        self.window = window
        self.last_cross_info = None
        self.cross_info_list = []
        self.cross_segment_list = []
        if self.hourly_mode:
            self.cross = Crossover2(window=self.window)
        else:
            self.cross = MTSCrossover2(win_secs=self.win_secs)
        self.cross_up= False
        self.cross_down = False

    def update(self, value1, value2, ts=0):
        self.cross.update(value1=value1, value2=value2, ts=ts)
        if self.cross.crossup_detected():
            if self.last_cross_info:
                if self.last_cross_info.type == CrossInfo.CROSS_UP:
                    return
                pchange = abs(100.0*(self.last_cross_info.value - self.cross.crossup_value) / self.last_cross_info.value)
                if pchange < 0.01:
                    return
            cross_info = CrossInfo(self.cross.crossup_value,
                                   self.cross.crossup_ts,
                                   CrossInfo.CROSS_UP)
            self.cross_info_list.append(cross_info)
            self.cross_up = True
            self.update_cross_segments()
            self.last_cross_info = cross_info
        elif self.cross.crossdown_detected():
            if self.last_cross_info:
                if self.last_cross_info.type == CrossInfo.CROSS_DOWN:
                    return
                pchange = abs(100.0*(self.last_cross_info.value - self.cross.crossdown_value) / self.last_cross_info.value)
                if pchange < 0.01:
                    return
            cross_info = CrossInfo(self.cross.crossdown_value,
                                   self.cross.crossdown_ts,
                                   CrossInfo.CROSS_DOWN)
            self.cross_info_list.append(cross_info)
            self.cross_down = False
            self.update_cross_segments()
            self.last_cross_info = cross_info

    def update_cross_segments(self):
        if len(self.cross_info_list) < 2:
            return
        start = self.cross_info_list[-2]
        end = self.cross_info_list[-1]
        segment = CrossSegmentInfo(start.value, end.value, start.ts, end.ts)
        self.cross_segment_list.append(segment)

    def cross_up_detected(self, clear=True):
        result = self.cross_up
        if clear:
            self.cross_up = False
        return result

    def cross_down_detected(self, clear=True):
        result = self.cross_down
        if clear:
            self.cross_down = False
        return result

    def get_cross_up_timestamps(self):
        timestamps = []
        for cross in self.cross_info_list:
            if cross.type == CrossInfo.CROSS_UP:
                timestamps.append(cross.ts)
        return timestamps

    def get_cross_down_timestamps(self):
        timestamps = []
        for cross in self.cross_info_list:
            if cross.type == CrossInfo.CROSS_DOWN:
                timestamps.append(cross.ts)
        return timestamps


class CrossInfo(object):
    CROSS_DOWN = -1
    CROSS_UP = 1

    def __init__(self, value, ts, type):
        self.value = value
        self.ts = ts
        self.type = type


class CrossSegmentInfo(object):
    def __init__(self, start_value, end_value, start_ts, end_ts):
        self.start_value = start_value
        self.end_value = end_value
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.percent = 0
        self.percent_per_hr = 0
        self.seconds = 0
        self.update_seconds()
        self.update_percent()
        self.update_percent_per_hr()

    def update_seconds(self):
        if not self.start_ts:
            return
        self.seconds = int((self.end_ts - self.start_ts) / 1000.0)

    def update_percent(self):
        if self.start_value:
            self.percent = round(100.0 * (self.end_value - self.start_value) / self.start_value, 2)

    def update_percent_per_hr(self):
        if not self.percent:
            return
        delta_hr = ((self.end_ts - self.start_ts) / 1000.0) / 3600.0
        if not delta_hr:
            return
        self.percent_per_hr = round(self.percent / delta_hr, 2)
