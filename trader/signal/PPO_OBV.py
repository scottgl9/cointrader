from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.PPO import PPO
from trader.lib.Crossover2 import Crossover2


class PPO_OBV(object):
    def __init__(self, win_short=12, win_med=26, win_long=50):
        self.signal_name = "PPO_OBV"
        self.id = 0
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.ppo = PPO(scale=24)
        self.obv = OBV()
        self.obv_ema12 = EMA(self.win_short, scale=24)
        self.obv_ema26 = EMA(self.win_med, scale=24)
        self.obv_ema50 = EMA(self.win_long, scale=24, lag_window=5)
        self.ppo_cross = Crossover2()

        self.buy_price = 0.0
        self.buy_size = 0.0
        self.buy_timestamp = 0
        self.buy_order_id = None
        self.last_buy_price = 0.0
        self.last_sell_price = 0.0

    def set_id(self, id):
        self.id = id

    def pre_update(self, close, volume):
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
