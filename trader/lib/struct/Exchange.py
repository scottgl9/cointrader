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
        if id == Exchange.EXCHANGE_BINANCE:
            return "binance"
        elif id == Exchange.EXCHANGE_CBPRO:
            return "cbpro"
        elif id == Exchange.EXCHANGE_BITTREX:
            return "bittrex"
        elif id == Exchange.EXCHANGE_KRAKEN:
            return "kraken"
        elif id == Exchange.EXCHANGE_POLONIEX:
            return "poloniex"
        elif id == Exchange.EXCHANGE_ROBINHOOD:
            return "robinhood"
        else:
            return "unknown"

    def id(name):
        if name == "binance":
            return Exchange.EXCHANGE_BINANCE
        elif name == "cbpro":
            return Exchange.EXCHANGE_CBPRO
        elif name == "bittrex":
            return Exchange.EXCHANGE_BITTREX
        elif name == "kraken":
            return Exchange.EXCHANGE_KRAKEN
        elif name == "poloniex":
            return Exchange.EXCHANGE_POLONIEX
        elif name == "robinhood":
            return Exchange.EXCHANGE_ROBINHOOD
        else:
            return Exchange.EXCHANGE_UNKNOWN