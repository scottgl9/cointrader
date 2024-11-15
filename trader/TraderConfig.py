import os
import sys
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser


class TraderConfig(object):
    def __init__(self, filename, exchange='binance', simulate=False):
        self.filename = filename
        self.exchange = exchange
        self.default_config_path = "config/defaults/{}.ini".format(self.exchange)
        self.simulate = simulate
        self.config = ConfigParser()
        self.config.optionxform = str
        self.section = None
        self.load()

    # load defaults from default config file for exchange
    def load_defaults(self, config, section):
        if not os.path.exists(self.default_config_path):
            print("{} doesn't exist, exiting...".format(self.default_config_path))
            sys.exit(-1)
        self.config.add_section(section)
        default_config = ConfigParser()
        default_config.read(self.default_config_path)
        for key, value in default_config.items(section):
            self.config.set(section, key, value)

    def load(self):
        config_updated = False
        if os.path.exists(self.filename):
            self.config.read(self.filename)

        section_name = "{}.live".format(self.exchange)
        if not self.section_exists(section_name):
            print("section {} doesn't exist, loading from {}".format(section_name, self.default_config_path))
            config_updated = True
            self.load_defaults(self.config, section_name)

        section_name = "{}.simulate".format(self.exchange)
        if not self.section_exists(section_name):
            print("section {} doesn't exist, loading from {}".format(section_name, self.default_config_path))
            config_updated = True
            self.load_defaults(self.config, section_name)

        if config_updated:
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

    # get value of specified option (section pre-set with select_section()
    def get(self, option):
        if not self.section:
            return None
        return self.get_section(self.section, option)

    # get value of specified option from specified section
    def get_section(self, section, option):
        result = self.config.get(section, option)
        if result == 'True':
            return True
        elif result == 'False':
            return False
        return result

    # return dict with all options with values in section
    def get_section_options(self, section=None):
        if not section:
            section = self.section
        return dict(self.config.items(section=section, raw=True))

    # return dict with all options for given field:
    # ex. field='balance', balance.BTC = 0.2
    # returns: {'BTC': 0.2 }
    def get_section_field_options(self, field, section=None):
        result = {}
        field = "{}.".format(field)
        options = self.get_section_options(section)
        for key in options.keys():
            if key.startswith(field):
                entry = key[len(field):].upper()
                result[entry] = options[key]
        return result

    def set(self, option, value):
        if not self.section:
            return
        self.config.set(self.section, option, value)
