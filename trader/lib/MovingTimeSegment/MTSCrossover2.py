# MTSCrossover version 2
# crossover detection
# 1) detect if values1 crosses from below to above values2 (crossup)
# 2) detect if values1 crosses from above to below values2 (crossdown)

from trader.lib.MovingTimeSegment.MTSCircularArray import MTSCircularArray


class MTSCrossover2(object):
    def __init__(self, win_secs=60):
        self.win_secs = win_secs
        self.mtsca1 = MTSCircularArray(win_secs=win_secs, max_win_size=win_secs+1, minmax=True)
        self.mtsca2 = MTSCircularArray(win_secs=win_secs, max_win_size=win_secs+1, minmax=True)
        self.crossup = False
        self.crossup_value = 0
        self.crossup_ts = 0
        self.crossdown = False
        self.crossdown_value = 0
        self.crossdown_ts = 0
        self.ts = 0

    def update(self, value1, value2, ts):
        if not self.ts:
            self.ts = ts

        self.mtsca1.add(value1, ts)
        self.mtsca2.add(value2, ts)

        if not self.mtsca1.ready():
            return

        mtsca2_last_value = self.mtsca2.last_value()
        if self.mtsca1.first_value() < mtsca2_last_value <= self.mtsca1.last_value():
            if self.crossup_ts and self.crossdown_ts < self.crossup_ts:
                return
            if self.mtsca1.last_value() == mtsca2_last_value:
                self.crossup_value = mtsca2_last_value
                self.crossup_ts = ts
            else:
                # find exact cross up point
                index_low = -1
                index_high = -1
                values = self.mtsca1.values(ordered=True)
                timestamps = self.mtsca1.timestamps(ordered=True)
                for i in range(len(values)-1, 0, -1):
                    if values[i] >= mtsca2_last_value: index_high = i
                    else: break
                for i in range(0, len(values)):
                    if values[i] <= mtsca2_last_value: index_low = i
                    else: break
                index = int((index_low + index_high) / 2)
                self.crossup_value = values[index]
                self.crossup_ts = timestamps[index]
            self.crossup = True
        elif self.mtsca1.first_value() >= mtsca2_last_value > self.mtsca1.last_value():
            if self.crossdown_ts and self.crossup_ts < self.crossdown_ts:
                return
            if self.mtsca1.first_value() == mtsca2_last_value:
                self.crossdown_value = mtsca2_last_value
                self.crossdown_ts = ts
            else:
                # find exact cross down point
                index_low = -1
                index_high = -1
                values = self.mtsca1.values(ordered=True)
                timestamps = self.mtsca1.timestamps(ordered=True)
                for i in range(len(values) - 1, 0, -1):
                    if values[i] <= mtsca2_last_value:
                        index_low = i
                    else:
                        break
                for i in range(0, len(values)):
                    if values[i] >= mtsca2_last_value:
                        index_high = i
                    else:
                        break
                index = int((index_low + index_high) / 2)
                self.crossdown_value = values[index]
                self.crossdown_ts = timestamps[index]
            self.crossdown = True

    # detect if value1 crosses up over value2
    def crossup_detected(self, clear=True):
        result = False
        if self.crossup:
            result = True
            if clear:
                self.crossup = False
        return result

    # detect if values1 crossed down under values2
    def crossdown_detected(self, clear=True):
        result = False
        if self.crossdown:
            result = True
            if clear:
                self.crossdown = False
        return result

    def clear(self):
        self.crossup = False
        self.crossdown = False
