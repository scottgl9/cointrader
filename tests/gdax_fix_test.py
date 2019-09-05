#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import base64
import time, datetime
import hmac
import sys
import hashlib
from gdax.FIX import FIX
#from gdax.settings import *

from trader.config import *

fix = FIX(GDAX_KEY_SB, GDAX_SECRET_SB, GDAX_PASS_SB, "FIX.4.2")
#fix.connect("127.0.0.1", 4197)
fix.start()
#while not fix.logged_in:
#    time.sleep(1)
#fix.order_status("*")
fix.stop()
fix.close()
sys.exit(0)
