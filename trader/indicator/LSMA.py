# linear least squares moving average
# https://stackoverflow.com/questions/5083465/fast-efficient-least-squares-fit-algorithm-in-c
import numpy as np

class LSMA(object):
    def __init__(self, window):
        self.window = window
        self.timestamps = []
        self.values = []
        self.age = 0
        self._sumx = 0
        self._sumx2 = 0
        self._sumxy = 0
        self._sumy = 0
        self._sumy2 = 0
        self.m = 0
        self.b = 0
        self.r = 0

    def ready(self):
        return len(self.values) == self.window

    def update(self, value, ts):
        if len(self.values) < self.window:
            self.values.append(float(value))
            self.timestamps.append(ts)
            self._sumx += float(ts)
            self._sumx2 += float(ts) * float(ts)
            self._sumxy += float(ts) * float(value)
            self._sumy += float(value)
            self._sumy2 += float(value) * float(value)
        else:
            last_x =  self.timestamps[int(self.age)]
            last_y = self.values[int(self.age)]
            self._sumx -= last_x
            self._sumx2 -= last_x * last_x
            self._sumxy -= last_x * last_y
            self._sumy -= last_y
            self._sumy2 -= last_y * last_y

            self.values[int(self.age)] = float(value)
            self.timestamps[int(self.age)] = int(ts)

            self._sumx += float(ts)
            self._sumx2 += float(ts) * float(ts)
            self._sumxy += float(ts) * float(value)
            self._sumy += float(value)
            self._sumy2 += float(value) * float(value)

            denom = (self.window * self._sumx2 - self._sumx * self._sumx)
            if denom == 0:
                # singular matrix, can't solve problem
                self.m = 0
                self.b = 0
                self.r = 0
                return

            self.m = (self.window * self._sumxy - self._sumx * self._sumy) / denom
            self.b = (self._sumy * self._sumx2 - self._sumx - self._sumxy) / denom

            # compute r
            r1 = self._sumxy - (self._sumx * self._sumy) / self.window
            r2 = np.sqrt((self._sumx2 - (self._sumx * self._sumx) / self.window) * (self._sumy2 - (self._sumy * self._sumy) / self.window))
            self.r = r1 / r2

        self.age = (self.age + 1) % self.window
