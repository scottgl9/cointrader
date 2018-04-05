from trader.strategy.buy_low_sell_high import buy_low_sell_high
from trader.strategy.fibonacci_with_macd import fibonacci_with_macd
from trader.strategy.macd_signal_strategy import macd_signal_strategy
from trader.strategy.quadratic_with_fibonacci import quadratic_with_fibonacci
from trader.strategy.smma_of_diff import smma_of_diff
from trader.strategy.order_book_strategy import order_book_strategy
from trader.strategy.trailing_prices_strategy import trailing_prices_strategy
from trader.strategy.momentum_swing_strategy import momentum_swing_strategy
from trader.strategy.macd_stop_order_follow import macd_stop_order_follow

def select_strategy(sname, client, name='BTC', currency='USD', account_handler=None, order_handler=None, base_min_size=0.0, tick_size=0.0):
    if sname == 'buy_low_sell_high':
        return buy_low_sell_high(client, name, currency, account_handler, order_handler)
    elif sname == 'fibonacci_with_macd':
        return fibonacci_with_macd(client, name, currency, account_handler, order_handler)
    elif sname == 'macd_signal_strategy':
        return macd_signal_strategy(client, name, currency, account_handler, order_handler)
    elif sname == 'quadratic_with_fibonacci':
        return quadratic_with_fibonacci(client, name, currency, account_handler, order_handler)
    elif sname == 'smma_of_diff':
        return smma_of_diff(client, name, currency, account_handler, order_handler)
    elif sname == 'order_book_strategy':
        return order_book_strategy(client, name, currency, account_handler, order_handler)
    elif sname == 'trailing_prices_strategy':
        return trailing_prices_strategy(client, name, currency, account_handler, order_handler)
    elif sname == 'momentum_swing_strategy':
        return momentum_swing_strategy(client, name, currency, account_handler, order_handler, base_min_size=base_min_size, tick_size=tick_size)
    elif sname == 'macd_stop_order_follow':
        return macd_stop_order_follow(client, name, currency, account_handler, order_handler, base_min_size=base_min_size, tick_size=tick_size)
