from trader.lib.Crossover2 import Crossover2
from trader.indicator.EMA import EMA

class global_obv_strategy(object):
    def __init__(self):
        self.obv_ema50_btc = EMA(50, scale=24)
        self.obv_ema100_btc = EMA(100, scale=24)
        self.obv_ema50_usdt = EMA(50, scale=24)
        self.obv_ema100_usdt = EMA(100, scale=24)

        self.cross_obv_btc = Crossover2(window=10)
        self.cross_obv_usdt = Crossover2(window=10)

        self.last_price = {}
        self.total_volume_btc = 0.0
        self.total_volume_usdt = 0.0
        self.result = 0
        self.disable_buy_btc = False

    def run_update(self, kline):
        symbol = kline.symbol
        close = kline.close
        volume = kline.volume

        if symbol.endswith('BTC'):
            if symbol not in self.last_price.keys():
                self.last_price[symbol] = close
            else:
                if close < self.last_price[symbol]:
                    self.total_volume_btc -= volume
                elif close > self.last_price[symbol]:
                    self.total_volume_btc += volume
                value1 = self.obv_ema50_btc.update(self.total_volume_btc)
                value2 = self.obv_ema100_btc.update(self.total_volume_btc)
                self.cross_obv_btc.update(value1, value2)
        elif symbol.endswith('USDT'):
            if symbol not in self.last_price.keys():
                self.last_price[symbol] = close
            else:
                if close < self.last_price[symbol]:
                    self.total_volume_usdt -= volume
                elif close > self.last_price[symbol]:
                    self.total_volume_usdt += volume
                value1 = self.obv_ema50_usdt.update(self.total_volume_usdt)
                value2 = self.obv_ema100_usdt.update(self.total_volume_usdt)
                self.cross_obv_usdt.update(value1, value2)

        if self.cross_obv_btc.crossdown_detected():
            self.disable_buy_btc = True
        elif self.cross_obv_btc.crossup_detected():
            self.disable_buy_btc = False

        self.last_price[symbol] = close

        return self.result
