from trader.strategy.macd_signal_strategy import macd_signal_strategy
from trader.strategy.quadratic_with_fibonacci import quadratic_with_fibonacci
from trader.strategy.smma_of_diff import smma_of_diff
from trader.strategy.order_book_strategy import order_book_strategy
from trader.strategy.momentum_swing_strategy import momentum_swing_strategy
from trader.strategy.null_strategy import null_strategy

def select_strategy(sname, client, name='BTC', currency='USD', account_handler=None, order_handler=None, base_min_size=0.0, tick_size=0.0, rank=None):
    if sname == 'macd_signal_strategy':
        return macd_signal_strategy(client, name, currency, account_handler, order_handler, base_min_size=base_min_size, tick_size=tick_size)
    elif sname == 'quadratic_with_fibonacci':
        return quadratic_with_fibonacci(client, name, currency, account_handler, order_handler)
    elif sname == 'smma_of_diff':
        return smma_of_diff(client, name, currency, account_handler, order_handler)
    elif sname == 'order_book_strategy':
        return order_book_strategy(client, name, currency, account_handler, order_handler)
    elif sname == 'momentum_swing_strategy':
        return momentum_swing_strategy(client, name, currency, account_handler, order_handler, base_min_size=base_min_size, tick_size=tick_size, rank=rank)
    elif sname == 'null_strategy':
        return null_strategy(client, name, currency, account_handler, order_handler, base_min_size=base_min_size, tick_size=tick_size)
