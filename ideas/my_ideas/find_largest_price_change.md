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
start_price_values = [0 : (max_price_ts - 1)]
mid_price_values = [max_price_ts : min_price_ts]
end_price_values = [(min_price_ts + 1) : -1]
```
2) if max_price_ts > min_price_ts (uptrend)
```
start_price_values = [0 : (min_price_ts - 1)]
mid_price_values = [min_price_ts : max_price_ts]
end_price_values = [(max_price_ts + 1) : -1]
```

define price_segment:
```
PRICE_SEGMENT {
    int start_ts;
    int end_ts;
    array prices;
    SPLIT_SEGMENT child; // subset of price segment
}

SPLIT_SEGMENT {
    PRICE_SEGMENT start_segment;
    PRICE_SEGMENT mid_segment;
    PRICE_SEGMENT end_segment;
}

```
Algorithm for building price segment structure:
```
divide_price_segments(price_values, ts_values, split_segment) 
{
    max_price = MAX(price_values)
    max_price_ts = ts_values[INDEX(max_price)]
    min_price = MAX(price_values)
    min_price_ts = ts_values[INDEX(max_price)]

    if max_price_ts < min_price_ts {
        start_price_values = [0 : (max_price_ts - 1)]
        mid_price_values = [max_price_ts : min_price_ts]
        end_price_values = [(min_price_ts + 1) : -1]
        mid_start_ts = max_price_ts
        mid_end_ts = min_price_ts
    } 
    if max_price_ts > min_price_ts {
        start_price_values = [0 : (min_price_ts - 1)]
        mid_price_values = [min_price_ts : max_price_ts]
        end_price_values = [(max_price_ts + 1) : -1]
        mid_start_ts = min_price_ts
        mid_end_ts = max_price_ts
    }

    start_segment=split_segment.start_segment
    mid_segment=split_segment.mid_segment
    end_segment=split_segment.end_segment

    start_segment.values=start_price_values
    start_segment.start_ts=0
    start_segment.end_ts=mid_start_ts-1

    mid_segment.values=mid_price_values
    mid_segment.start_ts=mid_start_ts
    mid_segment.end_ts=mid_end_ts
    
    end_segment.values=end_price_values
    end_segment.start_ts=mid_end_ts+1
    end_segment.end_ts=len(price_values)

    start_ts = ts_values[0]
    end_ts = ts_values[len(ts_values)]
    start_ts_values = ts_values[start_ts:mid_start_ts-1]
    mid_ts_values = ts_values[mid_start_ts:mid_end_ts]
    end_ts_values = ts_values[mid_end_ts:end_ts]

    divide_price_segments(start_price_values, start_ts_values, start_segment.child)
    divide_price_segments(mid_price_values, mid_ts_values, mid_segment.child)
    divide_price_segments(end_price_values, end_ts_values, end_segment.child)
}
```