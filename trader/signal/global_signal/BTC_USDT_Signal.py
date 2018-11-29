from trader.signal.SigType import SigType
from trader.signal.SignalBase import SignalBase
from trader.indicator.EMA import EMA
from trader.lib.MACross import MACross


class BTC_USDT_Signal(SignalBase):
    def __init__(self):
        super(BTC_USDT_Signal, self).__init__()
        self.signal_name = "BTC_USDT_Signal"
        self.global_signal = True
        self.global_filter = "BTCUSDT"
        self.ema_cross_250_500 = MACross(250, 500, scale=24, lag_window=5)
        self.disable_buy = False
        self.disable_sell = False
        self.enable_buy = True
        self.enable_sell = False

    def pre_update(self, close, volume, ts):
        self.ema_cross_250_500.update(close, ts)
        if (not self.disable_buy and self.ema_cross_250_500.cross_down and self.ema_cross_250_500.ma1_trend_down() and
                self.ema_cross_250_500.ma2_trend_down()):
            self.disable_buy = True
            self.enable_buy = False
        elif (not self.enable_buy and self.ema_cross_250_500.cross_up and self.ema_cross_250_500.ma1_trend_up() and
                self.ema_cross_250_500.ma2_trend_up()):
            self.disable_buy = False
            self.enable_buy = True
