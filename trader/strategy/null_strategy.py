from datetime import datetime
from trader.lib.struct.StrategyBase import StrategyBase


def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return float(total_seconds)


class null_strategy(StrategyBase):
    def __init__(self, client, base='BTC', currency='USD', account_handler=None, order_handler=None,
                 config=None, asset_info=None, logger=None):
        super(null_strategy, self).__init__(client,
                                            base,
                                            currency,
                                            account_handler,
                                            order_handler,
                                            asset_info,
                                            config,
                                            logger)
        self.strategy_name = 'null_strategy'
        signal_names = [self.config.get('signals')]
        #hourly_signal_name = self.config.get('rt_hourly_signal')
        self.last_price = self.price = 0.0
        self.rsi_result = 0.0
        self.last_rsi_result = 0.0
        #self.trend_tsi = MeasureTrend(window=20, detect_width=8, use_ema=False)

        self.base = base
        self.currency = currency

        self.buy_signal_count = self.sell_signal_count = 0
        self.high_24hr = self.low_24hr = 0.0
        self.open_24hr = self.close_24hr = self.volume_24hr = 0.0
        self.last_high_24hr = 0.0
        self.last_low_24hr = 0.0
        self.interval_price = 0.0
        self.last_buy_price = 0.0
        self.last_sell_price = 0.0
        self.count_prices_added = 0

        self.trend_upward_count = 0
        self.trend_downward_count = 0
        self.last_macd_diff = 0.0
        self.base_min_size = 0 #float(base_min_size)
        self.quote_increment = 0 #float(tick_size)
        self.buy_price_list = []
        self.buy_price = 0.0
        if not self.accnt.simulate:
            self.buy_price_list = self.accnt.load_buy_price_list(base, currency)
            if len(self.buy_price_list) > 0:
                self.buy_price = self.buy_price_list[-1]
        self.min_trade_size = self.base_min_size * 30.0
        #self.accnt.get_account_balances()

    def get_ticker_id(self):
        return self.ticker_id

    def html_run_stats(self):
        results = str('')
        results += "buy_signal_count: {}<br>".format(self.buy_signal_count)
        results += "sell_signal_count: {}<br>".format(self.sell_signal_count)
        return results

    def run_update(self, kline):
        pass
