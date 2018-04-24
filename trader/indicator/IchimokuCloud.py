
class IchimokuCloud(object):
    def __init__(self, win_short=12, win_med=26, win_long=50):
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.klows_short = []
        self.khighs_short = []
        self.klows_med = []
        self.khighs_med = []
        self.klows_long = []
        self.khighs_long = []
        self.close_prices = []

        self.last_klows_short = []
        self.last_khighs_short = []
        self.last_klows_med = []
        self.last_khighs_med = []
        self.last_klows_long = []
        self.last_khighs_long = []

        self.age_short = 0
        self.age_med = 0
        self.age_long = 0
        self.age_last_short = 0
        self.age_last_med = 0
        self.age_last_long = 0
        self.age_close = 0
        self.Tenkan_sen = 0.0
        self.Kijun_sen = 0.0
        self.Senkou_SpanA = 0.0
        self.Senkou_SpanB = 0.0
        self.close_last_window = 0.0

    def update(self, close, low, high):
        # update window size 9
        if len(self.klows_short) < self.win_short:
            self.klows_short.append(float(low))
            self.khighs_short.append(float(high))
        else:
            if len(self.last_klows_short) < self.win_short:
                self.last_klows_short.append(self.klows_short[int(self.age_short)])
                self.last_khighs_short.append(self.khighs_short[int(self.age_short)])
            else:
                self.last_klows_short[int(self.age_last_short)] = self.klows_short[int(self.age_short)]
                self.last_khighs_short[int(self.age_last_short)] = self.khighs_short[int(self.age_short)]

            self.klows_short[int(self.age_short)] = float(low)
            self.khighs_short[int(self.age_short)] = float(high)

            self.age_last_short = (self.age_last_short + 1) % self.win_short

        # update window size 26
        if len(self.klows_med) < self.win_med:
            self.klows_med.append(float(low))
            self.khighs_med.append(float(high))
        else:
            if len(self.last_klows_med) < self.win_med:
                self.last_klows_med.append(self.klows_med[int(self.age_med)])
                self.last_khighs_med.append(self.khighs_med[int(self.age_med)])
            else:
                self.last_klows_med[int(self.age_last_med)] = self.klows_med[int(self.age_med)]
                self.last_khighs_med[int(self.age_last_med)] = self.khighs_med[int(self.age_med)]

            self.klows_med[int(self.age_med)] = float(low)
            self.khighs_med[int(self.age_med)] = float(high)

            self.age_last_med = (self.age_last_med + 1) % self.win_med

        # update close prices
        if len(self.close_prices) < self.win_med:
            self.close_prices.append(close)
        else:
            self.close_last_window = self.close_prices[int(self.age_close)]
            self.close_prices[int(self.age_close)] = float(close)

        # update window size 52
        if len(self.klows_long) < self.win_long:
            self.klows_long.append(float(low))
            self.khighs_long.append(float(high))
        else:
            if len(self.last_klows_long) < self.win_long:
                self.last_klows_long.append(self.klows_long[int(self.age_long)])
                self.last_khighs_long.append(self.khighs_long[int(self.age_long)])
            else:
                self.last_klows_long[int(self.age_last_long)] = self.klows_long[int(self.age_long)]
                self.last_khighs_long[int(self.age_last_long)] = self.khighs_long[int(self.age_long)]

            self.klows_long[int(self.age_long)] = float(low)
            self.khighs_long[int(self.age_long)] = float(high)

            self.age_last_long = (self.age_last_long + 1) % self.win_long

        self.age_short = (self.age_short + 1) % self.win_short
        self.age_med = (self.age_med + 1) % self.win_med
        self.age_long = (self.age_long + 1) % self.win_long
        self.age_close = (self.age_close + 1) % self.win_med

        if len(self.last_klows_long) == 0:
            return 0, 0

        self.Tenkan_sen = (min(self.last_klows_short) + max(self.last_khighs_short)) / 2.0
        self.Kijun_sen = (min(self.last_klows_med) + max(self.last_khighs_med)) / 2.0
        self.Senkou_SpanA = (self.Tenkan_sen + self.Kijun_sen) / 2.0
        self.Senkou_SpanB = (min(self.last_klows_long) + max(self.last_khighs_long)) / 2.0

        return self.Senkou_SpanA, self.Senkou_SpanB