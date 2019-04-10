# linear least squares moving average
# https://stackoverflow.com/questions/5083465/fast-efficient-least-squares-fit-algorithm-in-c
import numpy as np

class LSMA(object):
    def __init__(self, window):
        self.window = window
        self.timestamps = []
        self.values = []
        self.age = 0
        self.start_ts = 0
        self._sumx = 0
        self._sumx2 = 0
        self._sumxy = 0
        self._sumy = 0
        self._sumy2 = 0
        self.m = 0
        self.b = 0
        self.r = 0
        self.n = 0
        self.result = 0

    def ready(self):
        return len(self.values) == self.window

    def update(self, value, ts):
        if not self.start_ts:
            self.start_ts = ts
        ts = float(ts - self.start_ts) / 1000.0

        if len(self.values) < self.window:
            self.values.append(float(value))
            self.timestamps.append(ts)
            self._sumx += ts
            self._sumx2 += ts * ts
            self._sumxy += ts * value
            self._sumy += value
            self._sumy2 += value * value
            self.result = value
            return self.result
        else:
            last_x =  self.timestamps[int(self.age)]
            last_y = self.values[int(self.age)]
            self._sumx -= last_x
            self._sumx2 -= last_x * last_x
            self._sumxy -= last_x * last_y
            self._sumy -= last_y
            self._sumy2 -= last_y * last_y

            self.values[int(self.age)] = value
            self.timestamps[int(self.age)] = ts

            self._sumx += ts
            self._sumx2 += ts * ts
            self._sumxy += ts * value
            self._sumy += value
            self._sumy2 += value * value

            self.n = self.window #max(self.timestamps) - min(self.timestamps)

            m2 = (self._sumx*self._sumx - self.n * self._sumx2)
            if m2 == 0:
                # singular matrix, can't solve problem
                self.m = 0
                self.b = 0
                self.r = 0
                self.result = float(value)
                return self.result

            m1 = (self._sumx * self._sumy - self.n * self._sumxy)

            self.m = m1 / m2
            self.b = (self._sumy - self.m * self._sumx) / self.n

            # compute r
            #r1 = self._sumxy - (self._sumx * self._sumy) / self.window
            #r2 = np.sqrt((self._sumx2 - (self._sumx * self._sumx) / self.window) * (self._sumy2 - (self._sumy * self._sumy) / self.window))
            #self.r = r1 / r2

        self.age = (self.age + 1) % self.window
        self.result = self.m * float(ts) + self.b

        return self.result
