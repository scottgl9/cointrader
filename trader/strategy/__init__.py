from trader.strategy.macd_signal_market_strategy import macd_signal_market_strategy
from trader.strategy.macd_signal_stop_loss_strategy import macd_signal_stop_loss_strategy
from trader.strategy.null_strategy import null_strategy

def select_strategy(sname, client, name='BTC', currency='USD', account_handler=None, order_handler=None, base_min_size=0.0, tick_size=0.0, rank=None, logger=None):
    if sname == 'macd_signal_market_strategy':
        return macd_signal_market_strategy(client, name, currency, account_handler, order_handler, base_min_size=base_min_size, tick_size=tick_size, logger=logger)
    elif sname == 'macd_signal_stop_loss_strategy':
        return macd_signal_stop_loss_strategy(client, name, currency, account_handler, order_handler, base_min_size=base_min_size, tick_size=tick_size, logger=logger)
    elif sname == 'null_strategy':
        return null_strategy(client, name, currency, account_handler, order_handler, base_min_size=base_min_size, tick_size=tick_size)
