from .IndicatorBase import IndicatorBase


class PSAR(IndicatorBase):
    def __init__(self, iaf=0.02, maxaf=0.2, close_only=False):
        IndicatorBase.__init__(self, use_close=True, use_low=True, use_high=True)
        self.iaf = iaf
        self.maxaf = maxaf
        self.af = 0
        self.bull = True
        self.psar = 0
        self.ep = 0
        self.hp = 0
        self.lp = 0
        self.psarbull = []
        self.psarbear = []
        self.prev_low = 0
        self.prev_high = 0
        self.last_prev_low = 0
        self.last_prev_high = 0
        self.close_only = close_only

    def update(self, close, low=0, high=0):
        # low and high values unavailable
        if self.close_only:
            low = close
            high = close

        if self.psar == 0 or self.last_prev_low == 0 or self.last_prev_high == 0:
            self.psar = close
            self.last_prev_low = self.prev_low
            self.last_prev_high = self.prev_high
            self.prev_low = low
            self.prev_high = high

            return self.psar

        prev_psar = self.psar

        if self.af == 0:
            self.af = self.iaf
        if self.ep == 0:
            self.ep = low
        if self.hp == 0:
            self.hp = high
        if self.lp == 0:
            self.lp = low

        if self.bull:
            self.psar = prev_psar + self.af * (self.hp - prev_psar)
        else:
            self.psar = prev_psar + self.af * (self.lp - prev_psar)

        reverse = False

        if self.bull:
            if low < self.psar:
                self.bull = False
                reverse = True
                self.psar = self.hp
                self.lp = low
                self.af = self.iaf
        else:
            if high > self.psar:
                self.bull = True
                reverse = True
                self.psar = self.lp
                self.hp = high
                self.af = self.iaf

        if not reverse:
            if self.bull:
                if high > self.hp:
                    self.hp = high
                    self.af = min(self.af + self.iaf, self.maxaf)
                if self.prev_low < self.psar:
                    self.psar = self.prev_low
                if self.last_prev_low < self.psar:
                    self.psar = self.last_prev_low
            else:
                if low < self.lp:
                    self.lp = low
                    self.af = min(self.af + self.iaf, self.maxaf)
                if self.prev_high > self.psar:
                    self.psar = self.prev_high
                if self.last_prev_high > self.psar:
                    self.psar = self.last_prev_high

        #if self.bull:
        #    self.psarbull.append(self.psar)
        #else:
        #    self.psarbear.append(self.psar)
        self.last_prev_low = self.prev_low
        self.last_prev_high = self.prev_high
        self.prev_low = low
        self.prev_high = high

        return self.psar
