class OrderUpdate(object):
    def __init__(self, symbol, price, stop_price, size, type, exec_type, side, ts, order_id, orig_id, status,
                 msg_type, msg_status):
        self.symbol = symbol
        self.price = price
        self.stop_price = stop_price
        self.size = size
        self.type = type
        self.exec_type = exec_type
        self.side = side
        self.ts = ts
        self.id = order_id
        self.orig_id = orig_id
        self.status = status
        self.msg_type = msg_type
        self.msg_status = msg_status

