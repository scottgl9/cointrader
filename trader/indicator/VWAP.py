# Volume weighted average price
# The theory is that if the price of a buy trade is lower than the VWAP, it is a good trade. The opposite is true if the price is higher than the VWAP.
# The VWAP is calculated by (SUM(number_shares_bought) * SharePrice) / total_shares_bought

# 1. Calculate the Typical Price for the period. [(High + Low + Close)/3)]
# 2. Multiply the Typical Price by the period Volume (Typical Price x Volume)
# 3. Create a Cumulative Total of Typical Price. Cumulative(Typical Price x Volume)
# 4. Create a Cumulative Total of Volume. Cumulative(Volume)
# 5. Divide the Cumulative Totals.
# VWAP = Cumulative(Typical Price x Volume) / Cumulative(Volume)


class VWAP:
    def __init__(self, window=60):
        self.volumes = []
        self.pricevolumes = []
        self.window = window
        self.age = 0
        self.typical_price_sum = 0.0
        self.pricevolume_sum = 0.0
        self.volume_sum = 0.0
        self.result = 0.0

    def kline_update(self, low, high, close, volume):
        pricevolume = ((high + low + close) / 3.0) * volume
        if len(self.pricevolumes) < self.window:
            tail_pricevolume = 0.0
            self.pricevolumes.append(float(pricevolume))
        else:
            tail_pricevolume = self.pricevolumes[self.age]
            self.pricevolumes[int(self.age)] = float(pricevolume)

        if len(self.volumes) < self.window:
            tail_volume = 0.0
            self.volumes.append(float(volume))
        else:
            tail_volume = self.volumes[self.age]
            self.volumes[int(self.age)] = float(volume)

        self.pricevolume_sum += float(pricevolume) - tail_pricevolume
        self.volume_sum += float(volume) - tail_volume
        self.age = (self.age + 1) % self.window

        if len(self.volumes) != 0 and len(self.pricevolumes) != 0:
            self.result = self.pricevolume_sum / self.volume_sum

        return self.result
