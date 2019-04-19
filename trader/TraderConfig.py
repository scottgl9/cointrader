import os
from ConfigParser import SafeConfigParser

class TraderConfig(object):
    def __init__(self, filename):
        self.filename = filename
        self.config = SafeConfigParser()
        self.section = None
        self.load()

    def set_defaults(self):
        section = 'binance.live'
        self.config.add_section(section)
        self.config.set(section, 'strategy', 'basic_signal_market_strategy')
        self.config.set(section, 'signals', 'Hybrid_Crossover_Test2')
        self.config.set(section, 'hourly_signal', 'Hourly_EMA_Crossover')
        self.config.set(section, 'hourly_kline_db_file', 'binance_hourly_klines.db')
        self.config.set(section, 'balance_update', 'True')
        self.config.set(section, 'use_hourly_klines', 'True')
        # live trading specific options
        self.config.set(section, 'btc_only', 'True')
        self.config.set(section, 'sell_only', 'False')
        self.config.set(section, 'trades_disabled', 'False')
        self.config.set(section, 'max_market_buy', '0')
        self.config.set(section, 'init_max_buy_count', '0')

        section = 'binance.simulate'
        self.config.add_section(section)
        self.config.set(section, 'strategy', 'basic_signal_market_strategy')
        self.config.set(section, 'signals', 'Hybrid_Crossover_Test2')
        self.config.set(section, 'hourly_signal', 'Hourly_EMA_Crossover')
        self.config.set(section, 'hourly_kline_db_file', 'binance_hourly_klines.db')
        self.config.set(section, 'balance_update', 'False')
        self.config.set(section, 'use_hourly_klines', 'True')
        # simulate trading specific options
        self.config.set(section, 'BTC', '0.2')
        self.config.set(section, 'ETH', '0.0')
        self.config.set(section, 'BNB', '0.0')
        self.config.set(section, 'btc_only', 'True')
        self.config.set(section, 'init_max_buy_count', '0')

    def load(self):
        if os.path.exists(self.filename):
            self.config.read(self.filename)
            return

        self.set_defaults()
        self.save()

    def reload(self):
        if not os.path.exists(self.filename):
            return
        self.config.read(self.filename)

    def save(self):
        with open(self.filename, 'w') as f:
            self.config.write(f)

    def select_section(self, section):
        self.section = section

    def get(self, option):
        if not self.section:
            return None
        return self.config.get(self.section, option)

    def get_section(self, section, option):
        return self.config.get(section, option)

    def set(self, option, value):
        if not self.section:
            return
        self.config.set(self.section, option, value)
        #self.save()
