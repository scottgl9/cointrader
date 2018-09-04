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
        for i in range(0, len(global_message_queue)):
            message = global_message_queue[i]
            if message.read:
                del global_message_queue[i]

    def add_message(self, src_id, dst_id, cmd, price=0.0, size=0.0, buy_price=0.0):
        msg = Message(src_id, dst_id, cmd, price, size, buy_price)
        global_message_queue.append(msg)

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

    def buy_market(self, ticker_id, price, size):
        self.add_message(ticker_id, Message.ID_MULTI, Message.MSG_MARKET_BUY, price, size)

    def sell_market(self, ticker_id, price, size, buy_price=0.0):
        self.add_message(ticker_id, Message.ID_MULTI, Message.MSG_MARKET_SELL, price, size, buy_price)

    def buy_stop_loss(self, ticker_id, price, size):
        self.add_message(ticker_id, Message.ID_MULTI, Message.MSG_STOP_LOSS_BUY, price, size)

    def sell_stop_loss(self, ticker_id, price, size, buy_price=0.0):
        self.add_message(ticker_id, Message.ID_MULTI, Message.MSG_STOP_LOSS_SELL, price, size, buy_price)
