User stream websocket - updates on binance account changes

## Order Update
Orders are updated with the `executionReport` event. Check the API documentation and below for relevant enum definitions.
Average price can be found by doing `Z` divided by `z`.

**Payload:**
```javascript
{
  "e": "executionReport",        // Event type
  "E": 1499405658658,            // Event time
  "s": "ETHBTC",                 // Symbol
  "c": "mUvoqJxFIILMdfAW5iGSOW", // Client order ID
  "S": "BUY",                    // Side
  "o": "LIMIT",                  // Order type
  "f": "GTC",                    // Time in force
  "q": "1.00000000",             // Order quantity
  "p": "0.10264410",             // Order price
  "P": "0.00000000",             // Stop price
  "F": "0.00000000",             // Iceberg quantity
  "g": -1,                       // Ignore
  "C": "null",                   // Original client order ID; This is the ID of the order being canceled
  "x": "NEW",                    // Current execution type
  "X": "NEW",                    // Current order status
  "r": "NONE",                   // Order reject reason; will be an error code.
  "i": 4293153,                  // Order ID
  "l": "0.00000000",             // Last executed quantity
  "z": "0.00000000",             // Cumulative filled quantity
  "L": "0.00000000",             // Last executed price
  "n": "0",                      // Commission amount
  "N": null,                     // Commission asset
  "T": 1499405658657,            // Transaction time
  "t": -1,                       // Trade ID
  "I": 8641984,                  // Ignore
  "w": true,                     // Is the order working? Stops will have
  "m": false,                    // Is this trade the maker side?
  "M": false,                    // Ignore
  "O": 1499405658657,            // Order creation time
  "Z": "0.00000000",             // Cumulative quote asset transacted quantity
  "Y": "0.00000000"              // Last quote asset transacted quantity (i.e. lastPrice * lastQty)
}
```

**Execution types:**

* NEW
* CANCELED
* REPLACED (currently unused)
* REJECTED
* TRADE
* EXPIRED

##### market buy order json response:
```
{u'orderId': 8034567,
 u'clientOrderId': u'2sJTFfa7Yqn6cR0zEzUDV1',
 u'origQty': u'40.00000000',
 u'fills': [{u'commission':
 u'0.00075369', u'price': u'0.06133000',
 u'commissionAsset': u'BNB',
 u'tradeId': 635730,
 u'qty': u'16.40000000'},
 {u'commission': u'0.00108459',
 u'price': u'0.06137000',
 u'commissionAsset': u'BNB',
 u'tradeId': 635731,
 u'qty': u'23.60000000'}],
 u'symbol': u'XRPBNB',
 u'side': u'BUY',
 u'timeInForce': u'GTC',
 u'status': u'FILLED',
 u'transactTime': 1546501907508,
 u'type': u'MARKET',
 u'price': u'0.00000000',
 u'executedQty': u'40.00000000',
 u'cummulativeQuoteQty': u'2.45414400'}
```
##### market sell order json response:
```
{u'orderId': 8016424,
 u'clientOrderId': u'OtM1BZTklrEsfLq8rCApK4',
 u'origQty': u'40.00000000',
 u'fills': [{u'commission':
 u'0.00183780', u'price': u'0.06126000',
 u'commissionAsset': u'BNB',
 u'tradeId': 634841,
 u'qty': u'40.00000000'}],
 u'symbol': u'XRPBNB',
 u'side': u'SELL',
 u'timeInForce': u'GTC',
 u'status': u'FILLED',
 u'transactTime': 1546464790804,
 u'type': u'MARKET',
 u'price': u'0.00000000',
 u'executedQty': u'40.00000000',
 u'cummulativeQuoteQty': u'2.45040000'}

```

### User message json responses (process_user_message() ):

##### set new limit order example:
```
{u'C': u'null',
 u'E': 1539567768296,
 u'F': u'0.00000000',
 u'I': 62115544,
 u'M': False,
 u'L': u'0.00000000',
 u'O': 1539567768294,
 u'N': None,
 u'P': u'0.00000000',
 u'S': u'SELL',
 u'T': 1539567768294,
 u'X': u'NEW',
 u'Z': u'0.00000000',
 u'c': u'and_0d75db6624ea47fca1a6ad363882d160',
 u'e': u'executionReport',
 u'g': -1,
 u'f': u'GTC',
 u'i': 29602101,
 u'm': False,
 u'l': u'0.00000000',
 u'o': u'LIMIT',
 u'n': u'0',
 u'q': u'0.25000000',
 u'p': u'0.04860000',
 u's': u'ETCETH',
 u'r': u'NONE',
 u't': -1,
 u'w': True,
 u'x': u'NEW',
 u'z': u'0.00000000'}

{u'b': 0, u'E': 1539567768296, u'D': True, u'm': 10, u's': 0, u'B': [{u'a': u'BTC', u'l': u'0.00000000', u'f': u'0.00002343'}, {u'a': u'LTC', u'l': u'0.00000000', u'f': u'0.54351498'}, {u'a': u'ETH', u'l': u'0.00000000', u'f': u'0.41534320'}, {u'a': u'NEO', u'l': u'0.00000000', u'f': u'0.00042700'}, {u'a': u'BNB', u'l': u'0.00000000', u'f': u'0.54067359'}, {u'a': u'123', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'456', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'QTUM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'EOS', u'l': u'0.00000000', u'f': u'0.00579000'}, {u'a': u'SNT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BNT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GAS', u'l': u'0.00000000', u'f': u'0.00491684'}, {u'a': u'BCC', u'l': u'0.00000000', u'f': u'0.08100825'}, {u'a': u'BTM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'USDT', u'l': u'0.00000000', u'f': u'0.00432212'}, {u'a': u'HCC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'HSR', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'OAX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DNT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MCO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ICN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ELC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ZRX', u'l': u'0.00000000', u'f': u'0.99600000'}, {u'a': u'OMG', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WTC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'YOYO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LRC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LLT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'TRX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SNGLS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'STRAT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BQX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'FUN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'KNC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CDT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XVG', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'IOTA', u'l': u'0.00000000', u'f': u'0.00058000'}, {u'a': u'SNM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LINK', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CVC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'TNT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'REP', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CTR', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MDA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MTL', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SALT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NULS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SUB', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MTH', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ADX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ETC', u'l': u'0.25000000', u'f': u'0.00460492'}, {u'a': u'ENG', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ZEC', u'l': u'0.00000000', u'f': u'0.11400000'}, {u'a': u'AST', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GNT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DGD', u'l': u'0.00000000', u'f': u'0.00013200'}, {u'a': u'BAT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DASH', u'l': u'0.00000000', u'f': u'0.18000000'}, {u'a': u'POWR', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BTG', u'l': u'0.00000000', u'f': u'0.24560001'}, {u'a': u'REQ', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XMR', u'l': u'0.00000000', u'f': u'0.28200000'}, {u'a': u'EVX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VIB', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ENJ', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VEN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ARK', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XRP', u'l': u'0.00000000', u'f': u'0.06970000'}, {u'a': u'MOD', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'STORJ', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'KMD', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'RCN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'EDO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DATA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DLT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MANA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'PPT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'RDN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GXS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'AMB', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ARN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BCPT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CND', u'l': u'0.00000000', u'f': u'0.00600000'}, {u'a': u'GVT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'POE', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BTS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'FUEL', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XZC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'QSP', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LSK', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BCD', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'TNB', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ADA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LEND', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XLM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CMT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WAVES', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WABI', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GTO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ICX', u'l': u'0.00000000', u'f': u'0.00393000'}, {u'a': u'OST', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ELF', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'AION', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WINGS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BRD', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NEBL', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NAV', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VIBE', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LUN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'TRIG', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'APPC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CHAT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'RLC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'INS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'PIVX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'IOST', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'STEEM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NANO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'AE', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VIA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BLZ', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SYS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'RPX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NCASH', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'POA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ONT', u'l': u'0.00000000', u'f': u'0.00039800'}, {u'a': u'ZIL', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'STORM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XEM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WAN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WPR', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'QLC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GRS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CLOAK', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LOOM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BCN', u'l': u'0.00000000', u'f': u'0.42652363'}, {u'a': u'TUSD', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ZEN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SKY', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'THETA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'IOTX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'QKC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'AGI', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NXS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NPXS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'KEY', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NAS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MFT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DENT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ARDR', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'HOT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VET', u'l': u'0.00000000', u'f': u'0.09740000'}, {u'a': u'DOCK', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'POLY', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VTHO', u'l': u'0.00000000', u'f': u'3.19472527'}, {u'a': u'ONG', u'l': u'0.00000000', u'f': u'0.01072509'}, {u'a': u'PHX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'HC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'PAX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'RVN', u'l': u'0.00000000', u'f': u'0.00000000'}], u'u': 1539567768296, u't': 10, u'W': True, u'e': u'outboundAccountInfo', u'T': True}
```
##
##### Cancel limit order example:
```
{u'C': u'and_0d75db6624ea47fca1a6ad363882d160',
 u'E': 1539567829766,
 u'F': u'0.00000000',
 u'I': 62115599,
 u'M': False,
 u'L': u'0.00000000',
 u'O': 1539567768294,
 u'N': None,
 u'P': u'0.00000000',
 u'S': u'SELL',
 u'T': 1539567829766,
 u'X': u'CANCELED',
 u'Z': u'0.00000000',
 u'c': u'android_fd1595de74164c01bd0f69b2a0de',
 u'e': u'executionReport',
 u'g': -1,
 u'f': u'GTC',
 u'i': 29602101,
 u'm': False,
 u'l': u'0.00000000',
 u'o': u'LIMIT',
 u'n': u'0',
 u'q': u'0.25000000',
 u'p': u'0.04860000',
 u's': u'ETCETH',
 u'r': u'NONE',
 u't': -1,
 u'w': False,
 u'x': u'CANCELED',
 u'z': u'0.00000000'}

{u'b': 0, u'E': 1539567829766, u'D': True, u'm': 10, u's': 0, u'B': [{u'a': u'BTC', u'l': u'0.00000000', u'f': u'0.00002343'}, {u'a': u'LTC', u'l': u'0.00000000', u'f': u'0.54351498'}, {u'a': u'ETH', u'l': u'0.00000000', u'f': u'0.41534320'}, {u'a': u'NEO', u'l': u'0.00000000', u'f': u'0.00042700'}, {u'a': u'BNB', u'l': u'0.00000000', u'f': u'0.54067359'}, {u'a': u'123', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'456', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'QTUM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'EOS', u'l': u'0.00000000', u'f': u'0.00579000'}, {u'a': u'SNT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BNT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GAS', u'l': u'0.00000000', u'f': u'0.00491684'}, {u'a': u'BCC', u'l': u'0.00000000', u'f': u'0.08100825'}, {u'a': u'BTM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'USDT', u'l': u'0.00000000', u'f': u'0.00432212'}, {u'a': u'HCC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'HSR', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'OAX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DNT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MCO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ICN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ELC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ZRX', u'l': u'0.00000000', u'f': u'0.99600000'}, {u'a': u'OMG', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WTC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'YOYO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LRC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LLT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'TRX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SNGLS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'STRAT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BQX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'FUN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'KNC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CDT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XVG', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'IOTA', u'l': u'0.00000000', u'f': u'0.00058000'}, {u'a': u'SNM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LINK', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CVC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'TNT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'REP', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CTR', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MDA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MTL', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SALT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NULS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SUB', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MTH', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ADX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ETC', u'l': u'0.00000000', u'f': u'0.25460492'}, {u'a': u'ENG', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ZEC', u'l': u'0.00000000', u'f': u'0.11400000'}, {u'a': u'AST', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GNT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DGD', u'l': u'0.00000000', u'f': u'0.00013200'}, {u'a': u'BAT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DASH', u'l': u'0.00000000', u'f': u'0.18000000'}, {u'a': u'POWR', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BTG', u'l': u'0.00000000', u'f': u'0.24560001'}, {u'a': u'REQ', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XMR', u'l': u'0.00000000', u'f': u'0.28200000'}, {u'a': u'EVX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VIB', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ENJ', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VEN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ARK', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XRP', u'l': u'0.00000000', u'f': u'0.06970000'}, {u'a': u'MOD', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'STORJ', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'KMD', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'RCN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'EDO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DATA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DLT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MANA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'PPT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'RDN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GXS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'AMB', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ARN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BCPT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CND', u'l': u'0.00000000', u'f': u'0.00600000'}, {u'a': u'GVT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'POE', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BTS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'FUEL', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XZC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'QSP', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LSK', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BCD', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'TNB', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ADA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LEND', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XLM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CMT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WAVES', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WABI', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GTO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ICX', u'l': u'0.00000000', u'f': u'0.00393000'}, {u'a': u'OST', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ELF', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'AION', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WINGS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BRD', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NEBL', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NAV', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VIBE', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LUN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'TRIG', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'APPC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CHAT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'RLC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'INS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'PIVX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'IOST', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'STEEM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NANO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'AE', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VIA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BLZ', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SYS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'RPX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NCASH', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'POA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ONT', u'l': u'0.00000000', u'f': u'0.00039800'}, {u'a': u'ZIL', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'STORM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'XEM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WAN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'WPR', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'QLC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GRS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'CLOAK', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'LOOM', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'BCN', u'l': u'0.00000000', u'f': u'0.42652363'}, {u'a': u'TUSD', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ZEN', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SKY', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'THETA', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'IOTX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'QKC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'AGI', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NXS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'SC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NPXS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'KEY', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'NAS', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'MFT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'DENT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'ARDR', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'HOT', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VET', u'l': u'0.00000000', u'f': u'0.09740000'}, {u'a': u'DOCK', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'POLY', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'VTHO', u'l': u'0.00000000', u'f': u'3.19472527'}, {u'a': u'ONG', u'l': u'0.00000000', u'f': u'0.01072509'}, {u'a': u'PHX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'HC', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'GO', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'PAX', u'l': u'0.00000000', u'f': u'0.00000000'}, {u'a': u'RVN', u'l': u'0.00000000', u'f': u'0.00000000'}], u'u': 1539567829766, u't': 10, u'W': True, u'e': u'outboundAccountInfo', u'T': True}
```
##
#### set new stop-loss buy order
```
{u'C': u'null',
 u'E': 1553986677346,
 u'F': u'0.00000000',
 u'I': 305969727,
 u'M': False,
 u'L': u'0.00000000',
 u'O': 1553986677341,
 u'N': None,
 u'P': u'0.00430000',
 u'S': u'BUY',
 u'T': 1553986677341,
 u'Y': u'0.00000000',
 u'X': u'NEW',
 u'Z': u'0.00000000',
 u'c': u'and_c5818cdaaadb4646b536c516486353f6',
 u'e': u'executionReport',
 u'g': -1,
 u'f': u'GTC',
 u'i': 133326357,
 u'm': False,
 u'l': u'0.00000000',
 u'o': u'STOP_LOSS_LIMIT',
 u'n': u'0',
 u'q': u'1.00000000',
 u'p': u'0.00430000',
 u's': u'BNBBTC',
 u'r': u'NONE',
 u't': -1,
 u'w': False,
 u'x': u'NEW',
 u'z': u'0.00000000'}
```
##
#### cancel stop-loss buy order
```
{u'C': u'and_c5818cdaaadb4646b536c516486353f6',
 u'E': 1553986687719,
 u'F': u'0.00000000',
 u'I': 305969847,
 u'M': False,
 u'L': u'0.00000000',
 u'O': 1553986677341,
 u'N': None,
 u'P': u'0.00430000',
 u'S': u'BUY',
 u'T': 1553986687715,
 u'Y': u'0.00000000',
 u'X': u'CANCELED',
 u'Z': u'0.00000000',
 u'c': u'and_b8ab4604b66746bfa5d04b038c6abf89',
 u'e': u'executionReport',
 u'g': -1,
 u'f': u'GTC',
 u'i': 133326357,
 u'm': False,
 u'l': u'0.00000000',
 u'o': u'STOP_LOSS_LIMIT',
 u'n': u'0',
 u'q': u'1.00000000',
 u'p': u'0.00430000',
 u's': u'BNBBTC',
 u'r': u'NONE',
 u't': -1,
 u'w': False,
 u'x': u'CANCELED',
 u'z': u'0.00000000'}
```
##
#### set new stop-loss sell order (REJECTED)
```
{u'C': u'null',
 u'E': 1553986709226,
 u'F': u'0.00000000',
 u'I': -1,
 u'M': False,
 u'L': u'0.00000000',
 u'O': -1,
 u'N': None,
 u'P': u'0.00300000',
 u'S': u'SELL',
 u'T': 1553986709221,
 u'Y': u'0.00000000',
 u'X': u'REJECTED',
 u'Z': u'0.00000000',
 u'c': u'and_80373484704e4efab489f7d6b56791b9',
 u'e': u'executionReport',
 u'g': -1,
 u'f': u'GTC',
 u'i': -1,
 u'm': False,
 u'l': u'0.00000000',
 u'o': u'STOP_LOSS_LIMIT',
 u'n': u'0',
 u'q': u'1.00000000',
 u'p': u'0.00300000',
 u's': u'BNBBTC',
 u'r': u'INSUFFICIENT_BALANCE',
 u't': -1,
 u'w': False,
 u'x': u'REJECTED',
 u'z': u'0.00000000'}
```
##
#### set new stop-loss sell order
```
{u'C': u'null',
 u'E': 1553986752283,
 u'F': u'0.00000000',
 u'I': 706734000,
 u'M': False,
 u'L': u'0.00000000',
 u'O': 1553986752279,
 u'N': None,
 u'P': u'3000.00000000',
 u'S': u'SELL',
 u'T': 1553986752279,
 u'Y': u'0.00000000',
 u'X': u'NEW',
 u'Z': u'0.00000000',
 u'c': u'and_874a642ad35f401288c1167da1d1f826',
 u'e': u'executionReport',
 u'g': -1,
 u'f': u'GTC',
 u'i': 302235564,
 u'm': False,
 u'l': u'0.00000000',
 u'o': u'STOP_LOSS_LIMIT',
 u'n': u'0',
 u'q': u'0.01000000',
 u'p': u'3000.00000000',
 u's': u'BTCUSDT',
 u'r': u'NONE',
 u't': -1,
 u'w': False,
 u'x': u'NEW',
 u'z': u'0.00000000'}
```
##
#### cancel stop-loss sell order
```
{u'C': u'and_874a642ad35f401288c1167da1d1f826',
 u'E': 1553986759205,
 u'F': u'0.00000000',
 u'I': 706734362,
 u'M': False,
 u'L': u'0.00000000',
 u'O': 1553986752279,
 u'N': None,
 u'P': u'3000.00000000',
 u'S': u'SELL',
 u'T': 1553986759199,
 u'Y': u'0.00000000',
 u'X': u'CANCELED',
 u'Z': u'0.00000000',
 u'c': u'and_f3acc7eca4ea4e70887db6a1ed9b96f6',
 u'e': u'executionReport',
 u'g': -1,
 u'f': u'GTC',
 u'i': 302235564,
 u'm': False,
 u'l': u'0.00000000',
 u'o': u'STOP_LOSS_LIMIT',
 u'n': u'0',
 u'q': u'0.01000000',
 u'p': u'3000.00000000',
 u's': u'BTCUSDT',
 u'r': u'NONE',
 u't': -1,
 u'w': False,
 u'x': u'CANCELED',
 u'z': u'0.00000000'}
```
##
#### Placed new TAKE_PROFIT_LIMIT order:
```
{u'C': u'null',
u'E': 1554408046996,
u'F': u'0.00000000',
u'I': 747350889,
u'M': False,
u'L': u'0.00000000',
u'O': 1554408046991,
u'N': None,
u'P': u'0.03208000',
u'S': u'BUY',
u'T': 1554408046991,
u'Y': u'0.00000000',
u'X': u'NEW',
u'Z': u'0.00000000',
u'c': u'and_3419f8e87cb44ab7a3c15957a79affcf',
u'e': u'executionReport',
u'g': -1,
u'f': u'GTC',
u'i': 319405041,
u'm': False,
u'l': u'0.00000000',
u'o': u'TAKE_PROFIT_LIMIT',
u'n': u'0',
u'q': u'0.10000000',
u'p': u'0.03208000',
u's': u'ETHBTC',
u'r': u'NONE',
u't': -1,
u'w': False,
u'x': u'NEW',
u'z': u'0.00000000'}

{u'C': u'null',
u'E': 1554408047352,
u'F': u'0.00000000',
u'I': 747350904,
u'M': False,
u'L': u'0.00000000',
u'O': 1554408046991,
u'N': None,
u'P': u'0.03208000',
u'S': u'BUY',
u'T': 1554408047347,
u'Y': u'0.00000000',
u'X': u'NEW',
u'Z': u'0.00000000',
u'c': u'and_3419f8e87cb44ab7a3c15957a79affcf',
u'e': u'executionReport',
u'g': -1,
u'f': u'GTC',
u'i': 319405041,
u'm': False,
u'l': u'0.00000000',
u'o': u'TAKE_PROFIT_LIMIT',
u'n': u'0',
u'q': u'0.10000000',
u'p': u'0.03208000',
u's': u'ETHBTC',
u'r': u'NONE',
u't': -1,
u'w': True,
u'x': u'NEW',
u'z': u'0.00000000'}
```
##
#### Filled TAKE_PROFIT_LIMIT order:
```
{u'C': u'null',
u'E': 1554408047918,
u'F': u'0.00000000',
u'I': 747350927,
u'M': True,
u'L': u'0.03208000',
u'O': 1554408046991,
u'N': u'BNB',
u'P': u'0.03208000',
u'S': u'BUY',
u'T': 1554408047916,
u'Y': u'0.00320800',
u'X': u'FILLED',
u'Z': u'0.00320800',
u'c': u'and_3419f8e87cb44ab7a3c15957a79affcf',
u'e': u'executionReport',
u'g': -1,
u'f': u'GTC',
u'i': 319405041,
u'm': True,
u'l': u'0.10000000',
u'o': u'TAKE_PROFIT_LIMIT',
u'n': u'0.00061233',
u'q': u'0.10000000',
u'p': u'0.03208000',
u's': u'ETHBTC',
u'r': u'NONE',
u't': 116162166,
u'w': False,
u'x': u'TRADE',
u'z': u'0.10000000'}
```
