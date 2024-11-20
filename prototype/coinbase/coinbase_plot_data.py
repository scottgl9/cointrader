import matplotlib.pyplot as plt
import requests
import json
import pandas as pd
from coinbase.rest import RESTClient
import time
import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.cbadv.AccountCoinbaseAdvanced import AccountCoinbaseAdvanced
from trader.config import *

MAX_CANDLES = 350

# pip3 install coinbase-advanced-py

def fetch_historical_data(product_id, granularity='ONE_HOUR', auto_adjust=True):
    # Validate granularity
    allowed_granularities = ['ONE_MINUTE', 'FIVE_MINUTE', 'FIFTEEN_MINUTE', 'ONE_HOUR', 'SIX_HOUR', 'ONE_DAY']
    granularity_mapping = {
        'ONE_MINUTE': 60,
        'FIVE_MINUTE': 300,
        'FIFTEEN_MINUTE': 900,
        'ONE_HOUR': 3600,
        'SIX_HOUR': 21600,
        'ONE_DAY': 86400
    }
    if granularity not in allowed_granularities:
        raise ValueError(f"Invalid granularity: {granularity}. Allowed values are {allowed_granularities}.")

    # Initialize Coinbase client
    client = RESTClient(api_key=Config.get_api_key(), api_secret=Config.get_api_secret())
    
    try:
        #print(client.get_products())
        # Set start to UNIX timestamp 24 hours ago, and end to current timestamp
        end = int(time.time())
        start = end - 48 * 3600
        # count the number of candles that will be retrieved based on start time, end time, and graularity
        num_candles = (end - start) // granularity_mapping[granularity]

        # If the number of candles exceeds the maximum allowed, adjust the start time
        if num_candles > MAX_CANDLES:
            if auto_adjust:
                start = end - MAX_CANDLES * granularity_mapping[granularity]
                num_candles = MAX_CANDLES
        print(num_candles)
        candles = client.get_candles(product_id, start, end, granularity=granularity)

        # get list of candles
        candles = candles['candles']
        #candles = [candle.__repr__() for candle in candles]
        candles = [candle.__dict__ for candle in candles]

        # Fetch historical data
        #candles = client.get_product_candles(product_id, granularity=granularity)
        
        # Convert the response into a DataFrame
        candles = json.dumps(candles)
        print(candles)
        numeric_columns = ['start', 'low', 'high', 'open', 'close', 'volume']
        df = pd.read_json(candles, orient='records')
        print(df)
        #df['start'] = pd.to_datetime(df['start'], unit='s')

        df[numeric_columns] = df[numeric_columns].astype(float)
        df.set_index('start', inplace=True)
        
        return df
    
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None


def plot_historical_data(data, title='Historical Data'):
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['close'], label='Close Price')
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

def main():
    product_id = 'BTC-USD'
    accnt = AccountCoinbaseAdvanced(simulate=False)
    klines = accnt.get_klines(days=1, hours=0, ticker_id=product_id, granularity=3600)
    klines = json.dumps(klines)
    print(klines)
    numeric_columns = ['start', 'low', 'high', 'open', 'close', 'volume']
    df = pd.read_json(klines, orient='records')
    #df['start'] = pd.to_datetime(df['start'], unit='s')

    df[numeric_columns] = df[numeric_columns].astype(float)
    df.set_index('start', inplace=True)

    # Plot historical data
    plot_historical_data(df, title=f'Historical Data for {product_id}')

if __name__ == "__main__":
    main()