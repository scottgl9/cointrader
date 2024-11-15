## Coinbase Pro API

## CBPRO full websocket results:
{
    "type": "match",
    "side": "buy",
    "product_id": "LINK-USD",
    "time": "2019-09-19T17:39:10.382000Z",
    "sequence": 291246433,
    "trade_id": 1099829,
    "maker_order_id": "f321783f-ce5a-40ca-95ad-695b112fc8e2",
    "taker_order_id": "6a0cf3c5-2225-4c60-9e96-86ab548e3614",
    "size": "141.63000000",
    "price": "1.8488"
}

{
    "type": "done",
    "side": "sell",
    "product_id": "LINK-USD",
    "time": "2019-09-19T17:39:10.382000Z",
    "sequence": 291246434,
    "order_id": "6a0cf3c5-2225-4c60-9e96-86ab548e3614",
    "reason": "filled",
    "price": "1.81259000",
    "remaining_size": "0.00000000"
}

{
    "type": "received",
    "side": "sell",
    "product_id": "LINK-USD",
    "time": "2019-09-19T17:39:10.382000Z",
    "sequence": 291246428,
    "order_id": "6a0cf3c5-2225-4c60-9e96-86ab548e3614",
    "order_type": "limit",
    "size": "541.63000000",
    "price": "1.81259000",
    "client_oid": "d3fc530d-2be6-4510-a293-3734d32082cb"
}

{
    "type": "open",
    "side": "buy",
    "product_id": "LINK-USD",
    "time": "2019-09-19T17:39:10.374000Z",
    "sequence": 291246426,
    "price": "1.83056",
    "order_id": "592ed2d5-7e3a-40dd-96b5-611d5f1aa06a",
    "remaining_size": "1500.00000000"
}

{
    "type": "subscriptions",
    "channels": [
        {
            "name": "full",
            "product_ids": [
                "LTC-USD",
                "BCH-USD",
                "ZEC-BTC",
                "XTZ-BTC",
                "BCH-BTC",
                "REP-BTC",
                "MANA-USDC",
                "ETH-USDC",
                "GNT-USDC",
                "ETC-USD",
                "EOS-BTC",
                "CVC-USDC",
                "BTC-USDC",
                "ETH-USD",
                "ZEC-USDC",
                "LOOM-USDC",
                "EOS-USD",
                "XRP-BTC",
                "DAI-USDC",
                "DNT-USDC",
                "BAT-ETH",
                "BTC-USD",
                "XTZ-USD",
                "LINK-ETH",
                "BAT-USDC",
                "LINK-USD",
                "ETH-DAI",
                "XLM-BTC",
                "DASH-BTC",
                "ALGO-USD",
                "LTC-BTC",
                "ETC-BTC",
                "ZRX-BTC",
                "ZRX-USD",
                "DASH-USD",
                "REP-USD",
                "XRP-USD",
                "XLM-USD",
                "ETH-BTC"
            ]
        }
    ]
}


# CBPRO: response funds to small with market_buy:
{'message': 'funds is too small. Minimum size is 10.00000000'}

# CBPRO: response place buy market order for BTC-USD with funds=10:
{
    "id": "b2e57bbf-586b-4e5a-80ea-7ff3bf8a9435",
    "product_id": "BTC-USD",
    "side": "buy",
    "stp": "dc",
    "funds": "9.97008973",
    "specified_funds": "10",
    "type": "market",
    "post_only": false,
    "created_at": "2019-09-19T15:56:51.219186Z",
    "fill_fees": "0",
    "filled_size": "0",
    "executed_value": "0",
    "status": "pending",
    "settled": false
}

# CBPRO: response place sell market order for BTC-USD with funds=10:
{
    "id": "bad2633c-48bf-4f31-9a32-fbf13795b094",
    "product_id": "BTC-USD",
    "side": "sell",
    "stp": "dc",
    "funds": "10",
    "specified_funds": "10",
    "type": "market",
    "post_only": false,
    "created_at": "2019-09-19T15:58:50.194704Z",
    "fill_fees": "0",
    "filled_size": "0",
    "executed_value": "0",
    "status": "pending",
    "settled": false
}

# CBPRO: place buy limit order for BTC-USD: client.place_limit_order(product_id='BTC-USD', side='buy', price='8000.0', size='0.01')
{
    "id": "3051e9fc-d761-46e7-8d51-dc238c17b1cd",
    "price": "8000",
    "size": "0.01",
    "product_id": "BTC-USD",
    "side": "buy",
    "stp": "dc",
    "type": "limit",
    "time_in_force": "GTC",
    "post_only": false,
    "created_at": "2019-09-19T16:01:48.120696Z",
    "fill_fees": "0",
    "filled_size": "0",
    "executed_value": "0",
    "status": "pending",
    "settled": false
}

# CBPRO cancel buy limit order for BTC-USD: client.cancel_order(order_id='3051e9fc-d761-46e7-8d51-dc238c17b1cd')
['3051e9fc-d761-46e7-8d51-dc238c17b1cd']

# CBPRO cancel buy limit order for non-existing order:
{'message': 'order not found'}

# CBPRO place sell limit order with insufficient funds:
{'message': 'Insufficient funds'}

# CBPRO place sell limit order client.place_limit_order(product_id='BTC-USD', side='sell', price='11000.0', size='0.01'):
{
    "id": "3b1d8780-3884-4f10-803e-a60ce432e493",
    "price": "11000",
    "size": "0.01",
    "product_id": "BTC-USD",
    "side": "sell",
    "stp": "dc",
    "type": "limit",
    "time_in_force": "GTC",
    "post_only": false,
    "created_at": "2019-09-19T16:09:22.430063Z",
    "fill_fees": "0",
    "filled_size": "0",
    "executed_value": "0",
    "status": "pending",
    "settled": false
}

# CBPRO get open limit order client.get_order(order_id='66cafb17-bebc-495b-9614-77837893f794'):
{
    "id": "66cafb17-bebc-495b-9614-77837893f794",
    "price": "11000.00000000",
    "size": "0.01000000",
    "product_id": "BTC-USD",
    "side": "sell",
    "type": "limit",
    "time_in_force": "GTC",
    "post_only": false,
    "created_at": "2019-09-19T16:12:33.593487Z",
    "fill_fees": "0.0000000000000000",
    "filled_size": "0.00000000",
    "executed_value": "0.0000000000000000",
    "status": "open",
    "settled": false
}

# CBPRO get open limit order not found client.get_order(order_id='66cafb17-bebc-495b-9614-77837893f794'):
{'message': 'NotFound'}

# CBPRO get open client orders:
    for order in client.get_orders(product_id='BTC-USD'):
        print(order)
{
    "id": "1f965905-5233-416c-b64e-cfaf06554de5",
    "price": "8000",
    "size": "0.01",
    "product_id": "BTC-USD",
    "side": "buy",
    "stp": "dc",
    "type": "limit",
    "time_in_force": "GTC",
    "post_only": false,
    "created_at": "2019-09-19T16:17:21.331995Z",
    "fill_fees": "0",
    "filled_size": "0",
    "executed_value": "0",
    "status": "pending",
    "settled": false
}
{
    "id": "1f965905-5233-416c-b64e-cfaf06554de5",
    "price": "8000.00000000",
    "size": "0.01000000",
    "product_id": "BTC-USD",
    "side": "buy",
    "type": "limit",
    "time_in_force": "GTC",
    "post_only": false,
    "created_at": "2019-09-19T16:17:21.331995Z",
    "fill_fees": "0.0000000000000000",
    "filled_size": "0.00000000",
    "executed_value": "0.0000000000000000",
    "status": "open",
    "settled": false
}
{
    "id": "66cafb17-bebc-495b-9614-77837893f794",
    "price": "11000.00000000",
    "size": "0.01000000",
    "product_id": "BTC-USD",
    "side": "sell",
    "type": "limit",
    "time_in_force": "GTC",
    "post_only": false,
    "created_at": "2019-09-19T16:12:33.593487Z",
    "fill_fees": "0.0000000000000000",
    "filled_size": "0.00000000",
    "executed_value": "0.0000000000000000",
    "status": "open",
    "settled": false
}

# CBPRO invalid buy stop order client.place_stop_order(product_id='BTC-USD', side='buy', price='11000.0', size='0.01'):
{'message': 'Invalid order_type stop'}
