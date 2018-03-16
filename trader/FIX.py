#!/usr/bin/python
import socket
import select
import base64
import time, datetime
import hmac
import hashlib
import collections
from uuid import uuid4
from trader.FIX42 import fixtags
from trader.FIX42 import msgtype
from gevent import monkey, queue #, socket
import gevent
import logging
import sys
#monkey.patch_socket()

class FIXMessage:
    def __init__(self, msg_type=None):
        self.header_parts = []
        self.body_parts = []
        self.msg_type = msg_type

    def __repr__(self):
        return self.string()

    def load(self, data):
        if not data:
            return
        parts = data.encode('utf-8').split("\x01")
        for part in parts:
            if '=' not in part: continue
            key, value = str(part).split('=', 1)
            self.body_parts.append((str(key), str(value)))

    def clear(self):
        self.header_parts = []
        self.body_parts = []

    def parse_response(self, data, header_name=True):
        self.clear()
        self.load(data)
        result = collections.OrderedDict()

        for tag, value in self.header_parts:
            if header_name:
                result[fixtags.tagToName(tag)] = value
            else:
                result[tag] = value

        for tag, value in self.body_parts:
            if header_name:
                result[fixtags.tagToName(tag)] = value
            else:
                result[tag] = value
        return result

    def get_body_field_names(self):
        names = []
        for tag, value in self.body_parts:
            names.append(fixtags.tagToName(tag))
        return names

    def get_body_field_names_values(self):
        names = {}
        for tag, value in self.body_parts:
            names[fixtags.tagToName(tag)] = value
        return names

    def set_header(self, field, value):
        #if field not in self.header_parts:
        self.header_parts.append((str(field), str(value)))

    def set(self, field, value):
        self.body_parts.append((str(field), str(value)))

    def prepend(self, field, value):
        self.body_parts.insert(0, (str(field), str(value)))

    def unset(self, fldnum):
        for (field, value) in self.body_parts:
            if field == fldnum:
                self.body_parts.remove((field, value))
                break

    def header(self):
        return ("|".join('{}={}'.format(str(key), str(value)) for key, value in self.header_parts)) + "|"

    def body(self):
        return ("|".join('{}={}'.format(str(key), str(value)) for key, value in self.body_parts)) + "|"

    def raw(self):
        return (self.header() + self.body()).replace("|", "\x01")

    def raw_values(self):
        values = []
        for key, value in self.body_parts:
            values.append(value)
        return "\x01".join(values)

    def body_length(self):
        return len(self.body())

# 8=FIX.4.2|9=101|35=1|52=20180218-22:43:58.286|49=Coinbase|56=7ab5327f0001506fae50eb49c55be966|34=3|112=1518993838286|10=069|
# [('BeginString', 'FIX.4.2'), ('BodyLength', '83'), ('MsgType', '0'), ('SendingTime', '20180218-22:43:43.285'),
#  ('SenderCompID', 'Coinbase'), ('TargetCompID', '7ab5327f0001506fae50eb49c55be966'), ('MsgSeqNum', '2'), ('CheckSum', '140')])

class FIX:
    def __init__(self, key, secret, passphrase, header, hostname="127.0.0.1", port=4197):
        self.header = header
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.s = None
        self.seqnum = 1
        self.queue = queue.Queue()
        self.worker_thread = None
        self.last_msg = None
        self.logged_in = False
        self.hostname = hostname
        self.port = port

    def start(self):
        self.worker_thread = gevent.spawn(self.worker)

    def stop(self):
        if self.worker_thread:
            gevent.joinall([self.worker_thread])

    def worker(self):
        print("starting worker")
        self.connect(self.hostname, self.port)
        self.logon()
        msg = FIXMessage()
        self.s.setblocking(0)
        while True:
            ready = select.select([self.s], [], [], 10)
            if ready[0]:
                data = self.s.recv(4096)
                if len(data) == 0:
                    break
            else:
            #    self.send_heartbeat()
                continue
            print("received:")
            print(data.replace("\x01", "|"))
            response = msg.parse_response(data)
            self.seqnum += 1
            sent_message = False
            if 'MsgType' in response:
                if response['MsgType'] == msgtype.LOGON:
                    self.logged_in = True
                #if response['MsgType'] == msgtype.HEARTBEAT:
                #    self.send_heartbeat()
                #    sent_message = True
                elif response['MsgType'] == msgtype.TESTREQUEST:
                    if 'TestReqID' in response:
                        self.send_heartbeat(response['TestReqID'])
                        sent_message = True
                    #else:
                    #    self.send_heartbeat()
                elif response['MsgType'] == msgtype.RESENDREQUEST:
                    new_message = FIXMessage(msgtype.SEQUENCERESET)

                    new_message.set(fixtags.GapFillFlag, 'N')
                    new_message.set(fixtags.NewSeqNo, response['BeginSeqNo'])
                    print("resending")
                    self.seqnum = int(response['BeginSeqNo'])
                    sent_message = True
                    self.send_message(new_message)
                print(response)
            if not sent_message and not self.queue.empty():
                print("sending new message")
                new_msg = self.queue.get()
                self.send_message(new_msg)
            time.sleep(1)

    def check_sum(self, msg):
        sum = 0
        for char in msg:
            sum += ord(char)
        sum = str(sum % 256)
        while len(sum) < 3:
            sum = '0' + sum
        return sum

    def connect(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

    def get_time(self):
        timestamp = str(time.time())
        return str(datetime.datetime.utcnow()).replace("-", "").replace(" ", "-")[:-3]

    def get_sequence_no(self):
        return str(self.seqnum)

    def _handleResendRequest(self, msg):
        protocol = self.codec.protocol
        responses = []

        beginSeqNo = msg[protocol.fixtags.BeginSeqNo]
        endSeqNo = msg[protocol.fixtags.EndSeqNo]
        if int(endSeqNo) == 0:
            endSeqNo = sys.maxsize
        logging.info("Received resent request from %s to %s", beginSeqNo, endSeqNo)
        replayMsgs = [] #self.engine.journaller.recoverMsgs(self.session, MessageDirection.OUTBOUND, beginSeqNo, endSeqNo)
        gapFillBegin = int(beginSeqNo)
        gapFillEnd = int(beginSeqNo)
        for replayMsg in replayMsgs:
            msgSeqNum = int(replayMsg[protocol.fixtags.MsgSeqNum])
            if replayMsg[protocol.fixtags.MsgType] in protocol.msgtype.sessionMessageTypes:
                gapFillEnd = msgSeqNum + 1
            else:
                if self.engine.shouldResendMessage(self.session, replayMsg):
                    if gapFillBegin < gapFillEnd:
                        # we need to send a gap fill message
                        gapFillMsg = FIXMessage(msgtype.SEQUENCERESET)
                        gapFillMsg.set(fixtags.GapFillFlag, 'Y')
                        gapFillMsg.set(fixtags.MsgSeqNum, gapFillBegin)
                        gapFillMsg.set(fixtags.NewSeqNo, str(gapFillEnd))
                        responses.append(gapFillMsg)

                    # and then resent the replayMsg
                    replayMsg.unset(fixtags.BeginString)
                    replayMsg.unset(fixtags.BodyLength)
                    replayMsg.unset(fixtags.SendingTime)
                    replayMsg.unset(fixtags.SenderCompID)
                    replayMsg.unset(fixtags.TargetCompID)
                    replayMsg.unset(fixtags.CheckSum)
                    replayMsg.set(fixtags.PossDupFlag, "Y")
                    responses.append(replayMsg)

                    gapFillBegin = msgSeqNum + 1
                else:
                    gapFillEnd = msgSeqNum + 1
                    responses.append(replayMsg)

        if gapFillBegin < gapFillEnd:
            # we need to send a gap fill message
            gapFillMsg = FIXMessage(protocol.msgtype.SEQUENCERESET)
            gapFillMsg.setField(protocol.fixtags.GapFillFlag, 'Y')
            gapFillMsg.setField(protocol.fixtags.MsgSeqNum, gapFillBegin)
            gapFillMsg.setField(protocol.fixtags.NewSeqNo, str(gapFillEnd))
            responses.append(gapFillMsg)

        return responses

    def add_message(self, msg):
        self.queue.put(msg)

    # [('BeginString', 'FIX.4.2'), ('BodyLength', '83'), ('MsgType', '0'), ('SendingTime', '20180218-22:43:43.285'),
    #  ('SenderCompID', 'Coinbase'), ('TargetCompID', '7ab5327f0001506fae50eb49c55be966'), ('MsgSeqNum', '2'), ('CheckSum', '140')])

    def send_message(self, msg):
        # need to do in reverse order:
        msg.prepend(fixtags.MsgSeqNum, self.get_sequence_no())
        msg.prepend(fixtags.TargetCompID, "Coinbase")
        msg.prepend(fixtags.SenderCompID, self.key)
        msg.prepend(fixtags.SendingTime, self.get_time())
        if msg.msg_type:
            msg.prepend(fixtags.MsgType, msg.msg_type)

        bodyLength = msg.body_length()
        #msg.unset(fixtags.MsgType)
        msg.set_header(fixtags.BeginString, self.header)
        msg.set_header(fixtags.BodyLength, bodyLength)

        #if msg.msg_type:
        #    msg.set_header(fixtags.MsgType, msg.msg_type)

        c_sum = self.check_sum(msg.raw())
        msg.set(fixtags.CheckSum, c_sum)
        self.last_msg = msg
        #print(msg.parse_response(msg.raw()))
        print(msg.raw().replace("\x01", "|"))
        self.s.sendall(msg.raw().encode('ascii'))
        self.seqnum += 1

    def logon(self):
        msg = FIXMessage(msgtype.LOGON)
        seq_num = "1"

        # The prehash string is the following fields joined by the FIX field separator (ASCII code 1): SendingTime, MsgType, MsgSeqNum, SenderCompID, TargetCompID, Password.
        msg.set(fixtags.SendingTime, self.get_time())
        msg.set(fixtags.MsgType, msgtype.LOGON)
        msg.set(fixtags.MsgSeqNum, self.get_sequence_no())
        msg.set(fixtags.SenderCompID, self.key)
        msg.set(fixtags.TargetCompID, "Coinbase")
        msg.set(fixtags.Password, self.passphrase)

        message = msg.raw_values().encode("utf-8")

        hmac_key = base64.b64decode(self.secret)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        sign_b64 = base64.b64encode(signature.digest()).decode()

        msg.clear()
        msg.set(fixtags.Password, self.passphrase)
        msg.set(fixtags.EncryptMethod, 0)
        msg.set(fixtags.HeartBtInt, 30)
        msg.set(fixtags.RawData, sign_b64)
        msg.set(fixtags.CancelOrdersOnDisconnect, 'Y')
        #bodyLength = msg.body_length()

        # remove msgType from body to use later in header
        #msg.unset(fixtags.MsgType)
        #msg.set_header(fixtags.BeginString,self.header)
        #msg.set_header(fixtags.SenderCompID, self.key)
        #msg.set_header(fixtags.TargetCompID, "Coinbase")
        #msg.set_header(fixtags.BodyLength, bodyLength)
        #msg.set_header(fixtags.MsgType, msgtype.LOGON)

        #c_sum = self.check_sum(msg.raw())

        #msg.set(fixtags.CheckSum, c_sum)
        #logon = msg.raw().encode('ascii')
        self.send_message(msg)

    def send_heartbeat(self, test_id=None):
        msg = FIXMessage(msgtype.HEARTBEAT)

        if test_id:
            msg.set(fixtags.TestReqID, test_id)

        print("Sending heartbeat TestReqID={}".format(test_id))
        self.send_message(msg)

    def send_test_request(self, test_id=None):
        msg = FIXMessage(msgtype.TESTREQUEST)

        if test_id:
            msg.set(fixtags.TestReqID, test_id)

        self.add_message(msg)

    def order_send(self, ordtype, side, price, amount, symbol):
        size = round(amount, 2)
        msg = FIXMessage(msgtype.NEWORDERSINGLE)
        #msg.set(fixtags.MsgType, msgtype.NEWORDERSINGLE)
        msg.set(fixtags.Symbol, symbol)
        msg.set(fixtags.ClOrdID, uuid4())
        msg.set(fixtags.Side, side)
        msg.set(fixtags.HandlInst, 1)
        msg.set(fixtags.TransactTime, self.get_time())
        msg.set(fixtags.OrdType, ordtype) # 2 = Limit
        msg.set(fixtags.OrderQty, size)
        msg.set(fixtags.Price, price)
        msg.set(fixtags.TimeInForce, '1') # 1 = GTC
        msg.set(7928, 'D') # STP
        self.add_message(msg)

    def order_cancel(self, ClOrdID, OrderID, Symbol):
        msg = FIXMessage(msgtype.ORDERCANCELREQUEST)
        #msg.set(fixtags.MsgType, msgtype.ORDERCANCELREQUEST)
        msg.set(fixtags.Symbol, Symbol)
        msg.set(fixtags.OrigClOrdID, ClOrdID)
        msg.set(fixtags.ClOrdID, 123456)
        msg.set(fixtags.OrderID, OrderID)
        self.add_message(msg)

    def order_status(self, order_id):
        msg = FIXMessage(msgtype.ORDERSTATUSREQUEST)
        #msg.set(fixtags.MsgType, msgtype.ORDERSTATUSREQUEST)
        msg.set(fixtags.OrderID, order_id)
        self.add_message(msg)

    def close(self):
        if self.s: self.s.close()
