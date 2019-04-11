class MTS_LSMA(object):
    def __init__(self, win_secs=1800):
        self.win_secs = win_secs
        self.win_secs_ts = win_secs #* 1000
        self.values = []
        self.timestamps = []
        self.start_ts = 0
        self._sumx = 0
        self._sumx2 = 0
        self._sumxy = 0
        self._sumy = 0
        self._sumy2 = 0
        self._sum_count = 0
        self.m1 = 0
        self.m2 = 0
        self.m = 0
        self.b = 0
        self.r = 0
        self.n = 0
        self.result = 0
        self.full = False
        self.start_ts = 0
        self.neg_slope_start_ts = 0
        self.pos_slope_start_ts = 0
        self.neg_slope_end_ts = 0
        self.pos_slope_end_ts = 0
        self.neg_slope_cnt = 0
        self.pos_slope_cnt = 0

    def ready(self):
        return self.full

    def update(self, value, ts):
        if not self.start_ts:
            self.start_ts = ts

        # adjust ts to seconds from start for correct slope value for m
        ts = float(ts - self.start_ts) / 1000.0

        self.values.append(value)
        self.timestamps.append(ts)

        self._sumx += ts
        self._sumx2 += ts * ts
        self._sumxy += ts * value
        self._sumy += value
        self._sumy2 += value * value
        self._sum_count += 1

        cnt = 0
        while (ts - self.timestamps[cnt]) > self.win_secs_ts:
            cnt += 1

        if cnt != 0:
            for i in range(0, cnt):
                last_x = self.timestamps[i]
                last_y = self.values[i]
                self._sumx -= last_x
                self._sumx2 -= last_x * last_x
                self._sumxy -= last_x * last_y
                self._sumy -= last_y
                self._sumy2 -= last_y * last_y
                self._sum_count -= 1

            self.timestamps = self.timestamps[cnt:]
            self.values = self.values[cnt:]
            if not self.full:
                self.full = True

        if not self.full:
            self.result = float(value)
            return self.result

        self.n = self._sum_count

        self.m2 = (self._sumx*self._sumx - self.n * self._sumx2)
        if self.m2 == 0:
            # singular matrix, can't solve problem
            self.m = 0
            self.b = 0
            self.r = 0
            self.result = float(value)
            return self.result

        self.m1 = (self._sumx * self._sumy - self.n * self._sumxy)

        self.m = self.m1 / self.m2
        self.b = (self._sumy - self.m * self._sumx) / self.n

        if self.m < 0:
            # if positive slope hasn't started or ended
            if not self.pos_slope_start_ts and not self.pos_slope_end_ts:
                # if also negative slope hasn't started or ended
                if not self.neg_slope_start_ts and not self.neg_slope_end_ts:
                    self.neg_slope_start_ts = ts
                    self.neg_slope_cnt = 1
                elif self.neg_slope_start_ts and not self.neg_slope_end_ts:
                    self.neg_slope_cnt += 1
            # if positive slope has started but hasn't ended
            elif self.pos_slope_start_ts and not self.pos_slope_end_ts:
                # negative slope has started but hasn't ended, so end positive slope, and begin negative slope
                if not self.neg_slope_start_ts and not self.neg_slope_end_ts:
                    # set as end of positive slope, and start of negative slope
                    self.pos_slope_end_ts = ts
                    self.neg_slope_start_ts = ts
                    self.neg_slope_cnt = 1
                else:
                    # negative slope started without ending positive slope, so reset all vars
                    self.pos_slope_start_ts = 0
                    self.pos_slope_end_ts = 0
                    self.pos_slope_cnt = 0
                    self.neg_slope_start_ts = 0
                    self.neg_slope_end_ts = 0
                    self.neg_slope_cnt = 0
        elif self.m > 0:
            # if negative slope hasn't started or ended
            if not self.neg_slope_start_ts and not self.neg_slope_end_ts:
                # if also positive slope hasn't started or ended
                if not self.pos_slope_start_ts and not self.neg_slope_end_ts:
                    self.pos_slope_start_ts = ts
                    self.pos_slope_cnt = 1
                elif self.pos_slope_start_ts and not self.pos_slope_end_ts:
                    self.pos_slope_cnt += 1
            # if negative slope has started but not ended
            elif self.neg_slope_start_ts and not self.neg_slope_end_ts:
                # positive slope has started but hasn't ended, so end negative slope, and begin positive slope
                if not self.pos_slope_start_ts and not self.pos_slope_end_ts:
                    # set as end of negative slope, and start of positive slope
                    self.neg_slope_end_ts = ts
                    self.pos_slope_start_ts = ts
                    self.pos_slope_cnt = 1
                else:
                    # positive slope started without ending negative slope, so reset all vars
                    self.pos_slope_start_ts = 0
                    self.pos_slope_end_ts = 0
                    self.pos_slope_cnt = 0
                    self.neg_slope_start_ts = 0
                    self.neg_slope_end_ts = 0
                    self.neg_slope_cnt = 0

        # compute r
        #r1 = self._sumxy - (self._sumx * self._sumy) / self.window
        #r2 = np.sqrt((self._sumx2 - (self._sumx * self._sumx) / self.window) * (self._sumy2 - (self._sumy * self._sumy) / self.window))
        #self.r = r1 / r2

        self.result = self.m * float(ts) + self.b
        return self.result
