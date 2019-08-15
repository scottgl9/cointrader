import numpy as np
from scipy.fftpack import rfft, irfft

class FourierFilter(object):
    def __init__(self, values=None, percent_hf_filter=80, cut_scalar=5):
        self.cut_scalar = float(cut_scalar)
        self.values = values
        self.signal = None
        self.hf_filter = float(percent_hf_filter) / 100.0

    def load(self, values):
        self.values = values

    def process(self):
        if type(self.values) == list:
            x = np.array(self.values)
        else:
            x = self.values

        t = np.arange(0, x.size)
        p = np.polyfit(t, x, 1)   # find trend in x
        notrend = x - p[0] * t     # detrended x
        freqdom = rfft(notrend)

        hf_filter = int(len(freqdom) * (1.0 - self.hf_filter))
        for i in range(hf_filter, len(freqdom)):
            freqdom[i] = 0

        self.signal = irfft(freqdom) + p[0] * t     # reverse transform and re-trend

        if self.cut_scalar:
            avg_delta = np.average(np.abs(self.values - self.signal))
            start_range = int(0.1 * len(self.signal))
            end_range = int((1.0 - 0.1) * len(self.signal))
            for i in range(0, len(self.signal)):
                if end_range > i > start_range:
                    continue
                if np.abs(self.values[i] - self.signal[i]) > self.cut_scalar * avg_delta:
                    self.signal[i] = self.values[i]

        return self.signal

    def get_result(self):
        return self.signal
