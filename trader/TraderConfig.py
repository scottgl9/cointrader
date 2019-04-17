import os
from ConfigParser import SafeConfigParser

class TraderConfig(object):
    def __init__(self, filename):
        self.filename = filename
        self.config = SafeConfigParser()
        self.section = None
        self.load()

    def set_defaults(self):
        self.config.add_section('binance.live')
        self.config.set('binance.live', 'strategy', 'basic_signal_market_strategy')
        self.config.set('binance.live', 'signals', 'Hybrid_Crossover_Test')
        self.config.set('binance.live', 'hourly_kline_db_file', 'binance_hourly_klines.db')
        self.config.set('binance.live', 'simulate', 'False')
        self.config.set('binance.live', 'balance_update', 'True')

        self.config.add_section('binance.simulate')
        self.config.set('binance.simulate', 'strategy', 'basic_signal_market_strategy')
        self.config.set('binance.simulate', 'signals', 'Hybrid_Crossover_Test')
        self.config.set('binance.simulate', 'hourly_kline_db_file', 'binance_hourly_klines.db')
        self.config.set('binance.simulate', 'simulate', 'True')
        self.config.set('binance.simulate', 'balance_update', 'False')
        self.config.set('binance.simulate', 'BTC', '0.2')
        self.config.set('binance.simulate', 'ETH', '0.0')
        self.config.set('binance.simulate', 'BNB', '0.0')

    def load(self):
        if os.path.exists(self.filename):
            self.config.read(self.filename)
            return

        self.set_defaults()
        self.save()

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
        self.save()
