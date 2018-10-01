from trader.indicator.ZLEMA import ZLEMA
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.signal.SignalBase import SignalBase

class sustained_volume_spike_signal(SignalBase):
    def __init__(self, window=50, factor=10, min_spike_count=5):
        super(sustained_volume_spike_signal, self).__init__()
        self.signal_name = "sustained_volume_spike_signal"
        self.window = window
        self.factor = float(factor)
        self.min_spike_count = min_spike_count
        self.test_avg_volume = 0
        self.volume_spike_count = 0
        self.test2_avg_volume = 0
        self.volume_drop_count = 0
        self.prev_avg_volume = 0
        self.avg_volume = 0
        self.volume = 0
        self.ema = EMA(self.window, scale=24)
        self.obv = OBV()
        self.obv_ema26 = EMA(26, scale=24, lag_window=5)
        self.obv_ema50 = EMA(50, scale=24, lag_window=5)

    def pre_update(self, close, volume, ts):
        self.volume = float(volume)
        obv_value = self.obv.update(close=close, volume=volume)
        self.obv_ema26.update(obv_value)
        self.obv_ema50.update(obv_value)

        self.prev_avg_volume = self.avg_volume

        result = self.ema.update(float(volume))
        self.avg_volume = result

        if self.test_avg_volume == 0 and (self.prev_avg_volume * self.factor) <= self.volume:
            self.test_avg_volume = self.prev_avg_volume
            self.volume_spike_count = 1
            #print("spike count {}".format(self.volume_spike_count))
        elif self.test2_avg_volume == 0 and self.prev_avg_volume > (self.factor * self.volume):
            self.test2_avg_volume = self.prev_avg_volume
            self.volume_drop_count = 1
            #print("drop count {}".format(self.volume_drop_count))
        elif self.test_avg_volume != 0:
            if (self.test_avg_volume * self.factor) <= self.volume:
                self.volume_spike_count += 1
                print("spike count {}".format(self.volume_spike_count))
            else:
                self.test_avg_volume = 0
                self.volume_spike_count = 0
        elif self.test2_avg_volume != 0:
            if self.test2_avg_volume > (self.factor * self.volume):
                self.volume_drop_count += 1
                print("drop count {}".format(self.volume_drop_count))
            else:
                self.test2_avg_volume = 0
                self.volume_drop_count = 0

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.obv_ema50.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
            return False

        if self.volume_spike_count >= self.min_spike_count:
            return True
        return False

    def sell_signal(self):
        if self.volume_drop_count >= self.min_spike_count:
            return True
        return False
