### Design of an algorithm which is able to find the largest price decrease, and largest price increase for the smallest time interval in a set of market price data 

#### Data descriptions
1) price_values: array containing prices to analyze
2) ts_values: array containing timestamps of prices in price_values where LEN(price_values) = LEN(ts_values)

max_price = MAX(price_values)
max_price_ts = ts_values[INDEX(max_price)]
min_price = MAX(price_values)
min_price_ts = ts_values[INDEX(max_price)]

now divide price_values based on min_price_ts, and max_price_ts into 3 parts:
1) if max_price_ts < min_price_ts: (downtrend)
```
start_price_values[0] = [0 : (max_price_ts - 1)]
mid_price_values[0] = [max_price_ts : min_price_ts]
end_price_values[0] = [(min_price_ts + 1) : -1]
```
2) if max_price_ts > min_price_ts (uptrend)
```
start_price_values[0] = [0 : (min_price_ts - 1)]
mid_price_values[0] = [min_price_ts : max_price_ts]
end_price_values[0] = [(max_price_ts + 1) : -1]
```

define price_segment:
```
price_segment {
    int start_ts;
    int end_ts;
    array prices_values;
    split_segment child_split_segment; // subset of price segment
}

split_segment {
    price_segment start_price_segment;
    price_segment mid_price_segment;
    price_segment end_price_segment;
}

```