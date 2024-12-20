# Average Directional Index Indicator (ADX)
from trader.lib.struct.IndicatorBase import IndicatorBase
from trader.indicator.ATR import ATR

# Formula:
# - upmove = high - high(-1)
# - downmove = low(-1) - low
# - +dm = upmove if upmove > downmove and upmove > 0 else 0
# - -dm = downmove if downmove > upmove and downmove > 0 else 0
# - +di = 100 * MovingAverage(+dm, period) / atr(period)
# - -di = 100 * MovingAverage(-dm, period) / atr(period)
# - dx = 100 * abs(+di - -di) / (+di + -di)
# - adx = MovingAverage(dx, period)


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
        self.pDM_values = []
        self._pDM_sum = 0
        self.pDM = 0
        # -DM values
        self.nDM_values = []
        self._nDM_sum = 0
        self.nDM = 0
        # +DI
        self.pDI = 0
        # -DI
        self.nDI = 0
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

        pDM = high - self.prev_high
        nDM = self.prev_low - low

        # - +dm = upmove if upmove > downmove and upmove > 0 else 0
        # - -dm = downmove if downmove > upmove and downmove > 0 else 0
        if pDM > nDM and pDM > 0:
            self.pDM = pDM
        else:
            self.pDM = 0.0
        if nDM > pDM and nDM > 0:
            self.nDM = nDM
        else:
            self.nDM = 0

        self.prev_low = low
        self.prev_high = high

        if len(self.pDM_values) < self.win or len(self.nDM_values) < self.win:
            self.pDM_values.append(self.pDM)
            self.nDM_values.append(self.nDM)
            self._pDM_sum += self.pDM
            self._nDM_sum += self.nDM
            return self.result
        else:
            if self.pDI and self.nDI:
                prev_pdm_sum = self._pDM_sum
                prev_ndm_sum = self._nDM_sum
                self._pDM_sum -= prev_pdm_sum / self.win
                self._pDM_sum += self.pDM
                self._nDM_sum -= prev_ndm_sum / self.win
                self._nDM_sum += self.nDM

            self.pDI = 100.0 * (self._pDM_sum / self.atr.result)
            self.nDI = 100.0 * (self._nDM_sum / self.atr.result)

        if not self.pDI and not self.nDI:
            return self.result

        dx = 100.0 * abs(self.pDI - self.nDI) / abs(self.pDI + self.nDI)
        if len(self.dx_values) < self.win:
            self.dx_values.append(dx)
            self._dx_sum += dx
            return self.result
        else:
            if not self.adx:
                self.adx = self._dx_sum / self.win
            else:
                prev_adx = self.adx
                self.adx = ((prev_adx * (self.win - 1.0)) + dx) / self.win

        self.result = self.adx
        return self.result
