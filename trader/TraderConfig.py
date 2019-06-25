import os
from ConfigParser import SafeConfigParser


class TraderConfig(object):
    def __init__(self, filename):
        self.filename = filename
        self.config = SafeConfigParser()
        self.section = None
        self.load()

    def set_defaults(self):
        path = os.path.join(os.path.basename(__file__), "..")
        section = 'binance.live'
        self.config.add_section(section)
        self.config.set(section, 'path', os.path.abspath(path))
        self.config.set(section, 'strategy', 'basic_signal_market_strategy')
        # available signal modes: hourly,realtime (comma separated)
        self.config.set(section, 'signal_modes', 'hourly,realtime')
        self.config.set(section, 'signals', 'Hybrid_Crossover_Test2')
        self.config.set(section, 'hourly_signal', 'Hourly_ROC_Signal')
        self.config.set(section, 'hourly_kline_db_file', 'binance_hourly_klines.db')
        self.config.set(section, 'hourly_preload_hours', '48')
        self.config.set(section, 'max_hourly_model_count', '5')

        self.config.set(section, 'simulate', 'False')
        self.config.set(section, 'store_trades', 'False')
        self.config.set(section, 'balance_update', 'True')
        self.config.set(section, 'use_hourly_klines', 'True')
        self.config.set(section, 'usdt_value_cutoff', '0.02')
        self.config.set(section, 'min_percent_profit', '1.0')
        # live trading specific options
        self.config.set(section, 'btc_only', 'False')
        self.config.set(section, 'eth_only', 'False')
        self.config.set(section, 'bnb_only', 'False')
        # only trade symbols present in hourly db
        self.config.set(section, 'hourly_symbols_only', 'True')
        #multi order strategy params
        self.config.set(section, 'multi_order_max_count', '5')
        # trade_size_strategy params
        self.config.set(section, 'btc_trade_size', '0.003')
        self.config.set(section, 'eth_trade_size', '0.1')
        self.config.set(section, 'bnb_trade_size', '1')
        self.config.set(section, 'pax_trade_size', '20')
        self.config.set(section, 'usdt_trade_size', '20')
        self.config.set(section, 'trade_size_multiplier', '5.0')

        self.config.set(section, 'sell_only', 'False')
        self.config.set(section, 'trades_disabled', 'False')
        self.config.set(section, 'max_market_buy', '0')
        self.config.set(section, 'init_max_buy_count', '0')

        section = 'binance.simulate'
        self.config.add_section(section)
        self.config.set(section, 'path', os.path.abspath(path))
        self.config.set(section, 'strategy', 'basic_signal_market_strategy')
        # available signal modes: hourly,realtime (comma separated)
        self.config.set(section, 'signal_modes', 'hourly,realtime')
        self.config.set(section, 'signals', 'Hybrid_Crossover_Test2')
        self.config.set(section, 'hourly_signal', 'Hourly_ROC_Signal')
        self.config.set(section, 'hourly_kline_db_file', 'binance_hourly_klines.db')
        self.config.set(section, 'hourly_preload_hours', '48')
        self.config.set(section, 'max_hourly_model_count', '5')

        self.config.set(section, 'simulate', 'True')
        self.config.set(section, 'store_trades', 'True')
        self.config.set(section, 'balance_update', 'False')
        self.config.set(section, 'use_hourly_klines', 'True')
        self.config.set(section, 'usdt_value_cutoff', '0.02')
        self.config.set(section, 'min_percent_profit', '1.0')
        # simulate trading specific options
        self.config.set(section, 'BTC', '0.2')
        self.config.set(section, 'ETH', '0.0')
        self.config.set(section, 'BNB', '0.0')
        self.config.set(section, 'btc_only', 'False')
        self.config.set(section, 'eth_only', 'False')
        self.config.set(section, 'bnb_only', 'False')
        # only trade symbols present in hourly db
        self.config.set(section, 'hourly_symbols_only', 'True')
        #multi order strategy params
        self.config.set(section, 'multi_order_max_count', '5')
        # trade_size_strategy params
        self.config.set(section, 'btc_trade_size', '0.004')
        self.config.set(section, 'eth_trade_size', '0.1')
        self.config.set(section, 'bnb_trade_size', '1')
        self.config.set(section, 'pax_trade_size', '20')
        self.config.set(section, 'usdt_trade_size', '20')
        self.config.set(section, 'trade_size_multiplier', '5.0')

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

    def section_exists(self, section):
        return self.config.has_section(section)

    def option_exists(self, option):
        return self.option_in_section_exists(self.section, option)

    def option_in_section_exists(self, section, option):
        return self.config.has_option(section, option)

    def get(self, option):
        if not self.section:
            return None
        return self.get_section(self.section, option)

    def get_section(self, section, option):
        result = self.config.get(section, option)
        if result == 'True':
            return True
        elif result == 'False':
            return False
        return result

    def set(self, option, value):
        if not self.section:
            return
        self.config.set(self.section, option, value)
        #self.save()
