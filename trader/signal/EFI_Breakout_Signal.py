from trader.signal.SignalBase import SignalBase
from trader.indicator.EFI import EFI
from trader.indicator.EMA import EMA
from trader.indicator.BB import BollingerBands
from trader.lib.Crossover import Crossover


class EFI_Breakout_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None):
        super(EFI_Breakout_Signal, self).__init__(accnt, symbol, asset_info)
        self.signal_name = "EFI_Breakout_Signal"
        #self.dtwma = DTWMA(window=30)
        self.efi = EFI(window=30, scale=24)
        self.bb = BollingerBands(dev_count=8.0, smoother=EMA(50, scale=24))
        self.efi_cross_high = Crossover(window=10)
        self.efi_cross_low = Crossover(window=10)

    def pre_update(self, close, volume, ts, cache_db=None):
        #self.dtwma.update(close, ts)
        self.efi.update(close, volume)
        self.bb.update(self.efi.result)
        self.efi_cross_high.update(self.bb.high_band, self.efi.result)
        self.efi_cross_low.update(self.bb.low_band, self.efi.result)

    def buy_signal(self):
        if self.efi_cross_high.crossup_detected():
            return True
        return False

    def sell_signal(self):
        if self.efi_cross_low.crossdown_detected():
            return True
        return False
