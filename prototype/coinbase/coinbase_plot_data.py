import requests
import pandas as pd
import matplotlib.pyplot as plt

import requests
import pandas as pd

from coinbase.rest import RESTClient
import pandas as pd
import time
from config import Config

# pip3 install coinbase-advanced-py

def fetch_historical_data(product_id, granularity='ONE_HOUR'):
    # Validate granularity
    allowed_granularities = ['ONE_MINUTE', 'FIVE_MINUTES', 'FIFTEEN_MINUTES', 'ONE_HOUR', 'SIX_HOURS', 'ONE_DAY']
    if granularity not in allowed_granularities:
        raise ValueError(f"Invalid granularity: {granularity}. Allowed values are {allowed_granularities}.")

    # Initialize Coinbase client
    client = RESTClient(api_key=Config.get_api_key(), api_secret=Config.get_api_secret())
    
    if 1:
        #print(client.get_products())
        # Set start to UNIX timestamp 24 hours ago, and end to current timestamp
        end = int(time.time())
        start = end - 24 * 3600
        candles = client.get_candles(product_id, start, end, granularity=granularity)
        # Fetch historical data
        #candles = client.get_product_candles(product_id, granularity=granularity)
        
        # Convert the response into a DataFrame
        print(candles['candles'])
        df = pd.read_json(candles['candles'], orient='columns')
        print(df['low'])
        #df['start'] = pd.to_datetime(df['start'], unit='s')
        numeric_columns = ['low', 'high', 'open', 'close', 'volume']
        df[numeric_columns] = df[numeric_columns].astype(float)
        #df.set_index('start', inplace=True)
        
        print(df)
        return df
    
    #except Exception as e:
    #    print(f"Error fetching historical data: {e}")
    #    return None


def plot_historical_data(data, title='Historical Data'):
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['close'], label='Close Price')
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

def main():
    # Define the trading pair and granularity (e.g., 3600 seconds = 1 hour)
    product_id = 'BTC-USD'
    granularity = 'ONE_HOUR'

    # Fetch historical data
    data = fetch_historical_data(product_id, granularity)
    print(data)

    # Plot historical data
    plot_historical_data(data, title=f'Historical Data for {product_id}')

if __name__ == "__main__":
    main()