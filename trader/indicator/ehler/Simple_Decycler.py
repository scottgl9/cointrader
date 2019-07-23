# https://www.tradingview.com/script/ZuIZPR4q-Ehlers-Simple-Decycler/
from trader.lib.struct.IndicatorBase import IndicatorBase
from trader.lib.struct.CircularArray import CircularArray
import math


class Simple_Decycler(IndicatorBase):
    def __init__(self, highpass_len=125, upper_percent=0.5, lower_percent=0.5):
        IndicatorBase.__init__(self, use_close=True)
        self.highpass_len = highpass_len
        self.upper_percent = upper_percent
        self.lower_percent = lower_percent

        # High - pass Filter
        PI = 2 * math.asin(1)
        self.alphaArg = 2 * PI / (self.highpass_len * math.sqrt(2))

        self.alpha = 0.0
        self.prev_alpha = 0.0
        self.src = CircularArray(window=3, dne=0)
        self.hp = CircularArray(window=3, dne=0)
        self.decycler = 0
        self.upper_band = 0
        self.lower_band = 0

    def update(self, value):
        self.prev_alpha = self.alpha

        if math.cos(self.alphaArg) != 0:
            self.alpha = (math.cos(self.alphaArg) + math.sin(self.alphaArg) - 1) / math.cos(self.alphaArg)
        elif self.prev_alpha != 0:
            self.alpha = self.prev_alpha

        self.src.add(float(value))

        hp = math.pow(1 - (self.alpha / 2), 2) * (self.src[0] - 2 * self.src[1] + self.src[2]) + 2 * (1 - self.alpha) * self.hp[1]
        hp -= math.pow(1 - self.alpha, 2) * self.hp[2]
        self.hp.add(hp)

        self.decycler = self.src[0] - self.hp[0]
        self.upper_band = (1 + self.upper_percent / 100) * self.decycler
        self.lower_band = (1 - self.lower_percent / 100) * self.decycler

        return self.decycler, self.lower_band, self.upper_band
