from trader.strategy.hybrid_signal_market_strategy import hybrid_signal_market_strategy
from trader.strategy.hybrid_signal_stop_loss_strategy import hybrid_signal_stop_loss_strategy
from trader.strategy.null_strategy import null_strategy

def select_strategy(sname, client, name='BTC', currency='USD', account_handler=None, base_min_size=0.0, tick_size=0.0, logger=None):
    if sname == 'hybrid_signal_market_strategy':
        return hybrid_signal_market_strategy(client, name, currency, account_handler,  base_min_size=base_min_size, tick_size=tick_size, logger=logger)
    elif sname == 'hybrid_signal_stop_loss_strategy':
        return hybrid_signal_stop_loss_strategy(client, name, currency, account_handler, base_min_size=base_min_size, tick_size=tick_size, logger=logger)
    elif sname == 'null_strategy':
        return null_strategy(client, name, currency, account_handler, base_min_size=base_min_size, tick_size=tick_size, logger=logger)
