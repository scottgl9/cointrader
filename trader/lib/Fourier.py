import numpy as np
import pylab as pl
from numpy import fft
import pandas as pd
from scipy.fftpack import rfft, irfft, rfftfreq


class FourierFit(object):
    def __init__(self, values=None, n_harm=10, cut_ends=True, cut_scalar=3.0):
        self.n_harm = n_harm        # number of harmonics in model
        # the beginning and end of the signal line will be significantly deviated
        # so if cut_ends is True, cut the deviated sections
        self.cut_ends = cut_ends
        self.cut_scalar = cut_scalar
        self.values = values
        self.signal = None

    def load(self, values):
        self.values = np.array(values)

    def process(self):
        if type(self.values) == list:
            x = np.array(self.values)
        else:
            x = self.values
        n = x.size
        t = np.arange(0, x.size)
        p = np.polyfit(t, x, 1)   # find trend in x
        x_notrend = x - p[0] * t            # detrended x
        x_freqdom = fft.fft(x_notrend)  # detrended x in frequency domain
        f = fft.fftfreq(n)
        indexes = list(range(n))             # frequencies
        # sort indexes by frequency, lower -> higher
        indexes.sort(key = lambda i: np.absolute(f[i]))
        self.signal = np.zeros(t.size)
        for i in indexes[:1 + self.n_harm * 2]:
            ampli = np.absolute(x_freqdom[i]) / n   # amplitude
            phase = np.angle(x_freqdom[i])          # phase
            self.signal += ampli * np.cos(2 * np.pi * f[i] * t + phase)
        self.signal += p[0] * t

        if self.cut_ends:
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


class FourierFilter(object):
    def __init__(self, values=None, percent_hf_filter=95, cut_ends=True, cut_scalar=3.0):
        self.cut_ends = cut_ends
        self.cut_scalar = cut_scalar
        self.values = values
        self.signal = None
        self.hf_filter = float(percent_hf_filter) / 100.0

    def load(self, values):
        self.values = np.array(values)

    def process(self):
        if type(self.values) == list:
            x = np.array(self.values)
        else:
            x = self.values
        n = x.size
        t = np.arange(0, x.size)
        p = np.polyfit(t, x, 1)   # find trend in x
        notrend = x - p[0] * t     # detrended x
        freqdom = rfft(notrend)
        #f = rfftfreq(n)
        #indices = list(range(n))
        #indices.sort(key=lambda i: np.absolute(f[i]))

        hf_filter = int(len(freqdom) * (1.0 - self.hf_filter))
        for i in range(hf_filter, len(freqdom)):
            freqdom[i] = 0

        self.signal = irfft(freqdom) + p[0] * t     # reverse transform and re-trend

        if self.cut_ends:
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
