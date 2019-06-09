from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.PPO import PPO
from trader.lib.Crossover import Crossover
from trader.lib.struct.SignalBase import SignalBase

class PPO_OBV(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, win_short=12, win_med=26, win_long=50):
        super(PPO_OBV, self).__init__(accnt, symbol, asset_info)
        self.signal_name = "PPO_OBV"
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.ppo = PPO(scale=24)
        self.obv = OBV()
        self.obv_ema12 = EMA(self.win_short, scale=24)
        self.obv_ema26 = EMA(self.win_med, scale=24)
        self.obv_ema50 = EMA(self.win_long, scale=24, lag_window=5)
        self.ppo_cross = Crossover()

    def pre_update(self, close, volume, ts=0, cache_db=None):
        obv_value = self.obv.update(close=close, volume=volume)
        self.obv_ema12.update(obv_value)
        self.obv_ema26.update(obv_value)
        self.obv_ema50.update(obv_value)

        self.ppo.update(close)
        self.ppo_cross.update(self.ppo.ppo, self.ppo.ppo_signal.result)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.obv_ema50.result > self.obv_ema50.last_result and self.ppo_cross.crossup_detected():
            return True
        return False

    def sell_signal(self):
        if self.obv_ema26.result <= self.obv_ema26.last_result and self.ppo_cross.crossdown_detected():
            return True
        return False
