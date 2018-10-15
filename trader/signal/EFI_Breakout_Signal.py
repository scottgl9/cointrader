from trader.signal.SigType import SigType
from trader.signal.SignalBase import SignalBase
from trader.indicator.EFI import EFI
from trader.indicator.BB import BollingerBands
from trader.lib.Crossover2 import Crossover2

class EFI_Breakout_Signal(SignalBase):
    def __init__(self):
        super(EFI_Breakout_Signal, self).__init__()
        self.signal_name = "EFI_Breakout_Signal"
        self.efi = EFI(window=13, scale=1)
        self.bb = BollingerBands(weight=10, dev_count=1.0, smoother=None)
        self.efi_cross_high = Crossover2(window=10, cutoff=0.0)
        self.efi_cross_low = Crossover2(window=10, cutoff=0.0)

    def pre_update(self, close, volume, ts):
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
