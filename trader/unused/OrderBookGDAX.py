from trader.OrderBookBase import OrderBookBase

class OrderBookGDAX(OrderBookBase):
    def __init__(self):
        self.bids_book = {}
        self.asks_book = {}

    def process_update(self, msg):
        if 'changes' in msg:
            for changes in msg['changes']:
                if changes[0] == 'buy':
                    self.bids_book[float(changes[1])] = float(changes[2])
                elif changes[0] == 'sell':
                    self.asks_book[float(changes[1])] = float(changes[2])

        elif 'asks' in msg or 'bids' in msg:
            if 'asks' in msg:
                for asks in msg['asks']:
                    self.asks_book[float(asks[0])] = float(asks[1])
            if 'bids' in msg:
                for bids in msg['bids']:
                    self.bids_book[float(bids[0])] = float(bids[1])
