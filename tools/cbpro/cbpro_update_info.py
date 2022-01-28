#!/usr/bin/env python3
# Update cbpro_info.json file

import sys
import json
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.cbpro.cbpro import AuthenticatedClient
from trader.account.cbpro.AccountCoinbasePro import AccountCoinbasePro
from trader.config import *

if __name__ == '__main__':
    client = AuthenticatedClient(CBPRO_KEY, CBPRO_SECRET, CBPRO_PASS)
    accnt = AccountCoinbasePro(client=client, simulate=False)
    output = json.dumps(accnt.get_exchange_info(), indent=4, sort_keys=True)

    with open('cbpro_info.json', 'w') as fout:
        fout.write(output)
    print("Updated cbpro_info.json")
