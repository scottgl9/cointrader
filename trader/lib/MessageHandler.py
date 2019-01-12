# global handling of messages to and from strategies to multitrader
from trader.lib.Message import Message

global_message_queue = []


class MessageHandler(object):
    def __init__(self):
        pass

    def empty(self):
        if len(global_message_queue) == 0:
            return True
        return False

    def clear(self):
        self.remove_by_dst_id(Message.ID_MULTI)

    def clear_read(self):
        if len(global_message_queue) == 0:
            return

        for message in global_message_queue:
            if message.read:
                global_message_queue.remove(message)

    def add(self, msg):
        global_message_queue.append(msg)

    def add_message(self, src_id, dst_id, cmd, sig_id, price=0.0, size=0.0, buy_price=0.0, ts=0,
                    asset_info=None, buy_type=0, sell_type=0):
        msg = Message(src_id, dst_id, cmd, sig_id, price, size, buy_price, ts,
                      asset_info, buy_type, sell_type)
        global_message_queue.append(msg)

    def get_first_message(self, src_id, dst_id, sig_id=0):
        if sig_id == 0:
            for msg in global_message_queue:
                if msg.dst_id == dst_id and msg.src_id == src_id:
                    return msg
        else:
            for msg in global_message_queue:
                if msg.dst_id == dst_id and msg.src_id == src_id and msg.sig_id == sig_id:
                    return msg

        return None

    def get_messages(self, src_id, dst_id):
        messages = []

        for message in global_message_queue:
            if message.dst_id == dst_id and message.src_id == src_id:
                messages.append(message)

        return messages

    # get all messages by id matching src_id or dst_id
    def get_messages_by_id(self, id):
        messages = []

        for message in global_message_queue:
            if message.dst_id == id or message.src_id == id:
                messages.append(message)

        return messages

    # get all messages by id matching src_id
    def get_messages_by_src_id(self, id):
        messages = []

        for message in global_message_queue:
            if message.src_id == id:
                messages.append(message)

        return messages

    # get all messages by id matching dst_id
    def get_messages_by_dst_id(self, id):
        messages = []

        for message in global_message_queue:
            if message.dst_id == id:
                messages.append(message)

        return messages

    # remove all messages by id matching src_id or dst_id
    def remove_by_id(self, id):
        for i in range(0, len(global_message_queue)):
            message = global_message_queue[i]
            if message.dst_id == id or message.src_id == id:
                del global_message_queue[i]

    # remove all messages by id matching src_id
    def remove_by_src_id(self, id):
        for i in range(0, len(global_message_queue)):
            message = global_message_queue[i]
            if message.src_id == id:
                del global_message_queue[i]

    # remove all messages by id matching dst_id
    def remove_by_dst_id(self, id):
        for i in range(0, len(global_message_queue)):
            #if i < len(global_message_queue) - 1:
            #    return
            message = global_message_queue[i]
            if message.dst_id == id:
                del global_message_queue[i]

    def buy_market(self, ticker_id, price, size, sig_id, asset_info=None, buy_type=0):
        self.add_message(src_id=ticker_id,
                         dst_id=Message.ID_MULTI,
                         cmd=Message.MSG_MARKET_BUY,
                         sig_id=sig_id,
                         price=price,
                         size=size,
                         asset_info=asset_info,
                         buy_price=buy_type)

    def sell_market(self, ticker_id, price, size, buy_price, sig_id, asset_info=None, sell_type=0):
        self.add_message(src_id=ticker_id,
                         dst_id=Message.ID_MULTI,
                         cmd=Message.MSG_MARKET_SELL,
                         sig_id=sig_id,
                         price=price,
                         size=size,
                         buy_price=buy_price,
                         asset_info=asset_info,
                         sell_type=sell_type)

    def buy_stop_loss(self, ticker_id, price, size, sig_id):
        self.add_message(src_id=ticker_id,
                         dst_id=Message.ID_MULTI,
                         cmd=Message.MSG_STOP_LOSS_BUY,
                         sig_id=sig_id,
                         price=price,
                         size=size)

    def sell_stop_loss(self, ticker_id, price, size, buy_price, sig_id):
        self.add_message(src_id=ticker_id,
                         dst_id=Message.ID_MULTI,
                         cmd=Message.MSG_STOP_LOSS_SELL,
                         sig_id=sig_id,
                         price=price,
                         size=size,
                         buy_price=buy_price)

    def buy_complete(self, ticker_id, price, size, sig_id):
        self.add_message(src_id=Message.ID_MULTI,
                         dst_id=ticker_id,
                         cmd=Message.MSG_BUY_COMPLETE,
                         sig_id=sig_id,
                         price=price,
                         size=size)

    def sell_complete(self, ticker_id, price, size, buy_price, sig_id):
        self.add_message(src_id=Message.ID_MULTI,
                         dst_id=ticker_id,
                         cmd=Message.MSG_SELL_COMPLETE,
                         sig_id=sig_id,
                         price=price,
                         size=size,
                         buy_price=buy_price)

    def buy_failed(self, ticker_id, price, size, sig_id):
        self.add_message(src_id=Message.ID_MULTI,
                         dst_id=ticker_id,
                         cmd=Message.MSG_BUY_FAILED,
                         sig_id=sig_id,
                         price=price,
                         size=size)

    def sell_failed(self, ticker_id, price, size, buy_price, sig_id):
        self.add_message(src_id=Message.ID_MULTI,
                         dst_id=ticker_id,
                         cmd=Message.MSG_SELL_FAILED,
                         sig_id=sig_id,
                         price=price,
                         size=size,
                         buy_price=buy_price)

    def buy_replace(self, ticker_id, price, size, sig_id):
        self.add_message(src_id=ticker_id,
                         dst_id=Message.ID_MULTI,
                         cmd=Message.MSG_BUY_REPLACE,
                         sig_id=sig_id,
                         price=price,
                         size=size)

    def sell_replace(self, ticker_id, price, size, buy_price, sig_id):
        self.add_message(src_id=ticker_id,
                         dst_id=Message.ID_MULTI,
                         cmd=Message.MSG_SELL_REPLACE,
                         sig_id=sig_id,
                         price=price,
                         size=size,
                         buy_price=buy_price)

    def buy_update(self, ticker_id, price, size, sig_id=0, ts=0):
        self.add_message(src_id=ticker_id,
                         dst_id=Message.ID_ROOT,
                         cmd=Message.MSG_BUY_UPDATE,
                         sig_id=sig_id,
                         price=price,
                         size=size,
                         ts=ts)

    def buy_disable(self, ticker_id, sig_id=0, ts=0):
        self.add_message(src_id=ticker_id,
                         dst_id=Message.ID_MULTI,
                         cmd=Message.MSG_BUY_DISABLE,
                         sig_id=sig_id,
                         price=0,
                         size=0,
                         ts=ts)

    def buy_enable(self, ticker_id, sig_id=0, ts=0):
        self.add_message(src_id=ticker_id,
                         dst_id=Message.ID_MULTI,
                         cmd=Message.MSG_BUY_ENABLE,
                         sig_id=sig_id,
                         price=0,
                         size=0,
                         ts=ts)

    def sell_update(self, ticker_id, price, size, buy_price, sig_id=0, ts=0):
        self.add_message(src_id=ticker_id,
                         dst_id=Message.ID_ROOT,
                         cmd=Message.MSG_SELL_UPDATE,
                         sig_id=sig_id,
                         price=price,
                         size=size,
                         buy_price=buy_price,
                         ts=ts)

    def order_size_update(self, ticker_id, price, size, sig_id):
        self.add_message(src_id=Message.ID_MULTI,
                         dst_id=ticker_id,
                         cmd=Message.MSG_ORDER_SIZE_UPDATE,
                         sig_id=sig_id,
                         price=price,
                         size=size)
