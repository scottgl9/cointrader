# Supported exchanges

class Exchange(object):
    EXCHANGE_UNKNOWN = 0
    EXCHANGE_BINANCE = 1
    EXCHANGE_CBPRO = 2
    EXCHANGE_BITTREX = 3
    EXCHANGE_KRAKEN = 4
    EXCHANGE_POLONIEX = 5
    EXCHANGE_ROBINHOOD = 6

    def name(id):
        if id == EXCHANGE_BINANCE:
            return "binance"
        elif id == EXCHANGE_CBPRO:
            return "cbpro"
        elif id == EXCHANGE_BITTREX:
            return "bittrex"
        elif id == EXCHANGE_KRAKEN:
            return "kraken"
        elif id == EXCHANGE_POLONIEX:
            return "poloniex"
        elif id == EXCHANGE_ROBINHOOD:
            return "robinhood"
        else:
            return "unknown"

    def id(name):
        if name == "binance":
            return EXCHANGE_BINANCE
        elif name == "cbpro":
            return EXCHANGE_CBPRO
        elif name == "bittrex":
            return EXCHANGE_BITTREX
        elif name == "kraken":
            return EXCHANGE_KRAKEN
        elif name == "poloniex":
            return EXCHANGE_POLONIEX
        elif name == "robinhood":
            return EXCHANGE_ROBINHOOD
        else:
            return EXCHANGE_UNKNOWN
