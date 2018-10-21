#!/usr/bin/python
import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader
import logging
from trader.lib.TraderDB import TraderDB

if __name__ == '__main__':
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)

    traderdb = TraderDB(filename="trade.db", logger=logger)
    traderdb.connect()
    logger.info("Trade count={}".format(traderdb.get_trade_count_total()))
    traderdb.close()
