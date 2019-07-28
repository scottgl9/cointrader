# Average Directional Index Indicator (ADX)
from trader.lib.struct.IndicatorBase import IndicatorBase
from trader.indicator.ATR import ATR


class ADX(IndicatorBase):
    def __init__(self, win=14.0):
        IndicatorBase.__init__(self, use_close=True, use_low=True, use_high=True)
        self.win = win
        self.atr = ATR(window=self.win)
        self.adx = 0
        self.dx_values = []
        self.dx_age = 0
        self._dx_sum = 0
        # +DM values
        self.pdm_values = []
        self._pdm_sum = 0
        self.pdm = 0
        # -DM values
        self.ndm_values = []
        self._ndm_sum = 0
        self.ndm = 0
        # +DI
        self.pdi = 0
        # -DI
        self.ndi = 0
        self.dm_age = 0
        self.prev_low = 0
        self.prev_high = 0
        self.result = 0

    def update(self, close, low, high):
        self.atr.update(close, low, high)

        if not self.prev_low or not self.prev_high:
            self.prev_low = low
            self.prev_high = high
            return self.result

        self.pdm = high - self.prev_high
        self.ndm = self.prev_low - low

        self.prev_low = low
        self.prev_high = high

        if len(self.pdm_values) < self.win or len(self.ndm_values) < self.win:
            self.pdm_values.append(self.pdm)
            self.ndm_values.append(self.ndm)
            self._pdm_sum += self.pdm
            self._ndm_sum += self.ndm
            return self.result
        else:
            self._pdm_sum -= self.pdm_values[int(self.dm_age)]
            self._pdm_sum += self.pdm
            self._ndm_sum -= self.ndm_values[int(self.dm_age)]
            self._ndm_sum += self.ndm
            self.pdm_values[int(self.dm_age)] = self.pdm
            self.ndm_values[int(self.dm_age)] = self.ndm
            self.dm_age = (self.dm_age + 1) % self.win

        smooth_pdm = self._pdm_sum - self._pdm_sum / 14.0 + self.pdm
        smooth_ndm = self._ndm_sum - self._ndm_sum / 14.0 + self.ndm

        self.pdi = (smooth_pdm / self.atr.result) * 100.0
        self.ndi = (smooth_ndm / self.atr.result) * 100.0

        dx = 100.0 * abs(self.pdi - self.ndi) / abs(self.pdi + self.ndi)
        if len(self.dx_values) < self.win:
            self.dx_values.append(dx)
            self._dx_sum += dx
            return self.result
        else:
            self._dx_sum -= self.dx_values[int(self.dx_age)]
            self._dx_sum += dx
            self.dx_values[int(self.dx_age)] = dx
            self.dx_age = (self.dx_age + 1) % self.win

        if not self.adx:
            self.adx = self._dx_sum / self.win
        else:
            prev_adx = self.adx
            self.adx = ((prev_adx * (self.win - 1.0)) + dx) / self.win

        self.result = self.adx
        return self.result
