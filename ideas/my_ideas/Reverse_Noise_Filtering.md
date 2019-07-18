# Reverse noise filtering by time segments

The idea is to use TimeSegmentValues class in order to characterize noise in various segments of time, and using
smallest time segment (ts0) with noise profile n0, to filter larger time segment ts1, such that:

n0 = get_noise(ts0)
result0 = filter(ts1, n0)
n1 = get_noise(ts1)
result1 = filter(ts2, n1)
n2 = get_noise(ts2)
result3 = filter(ts3, n2)
....

Lets say ts0 is a 1m time interval of price values, ts1 is 5m, ts2 is 15m, ts3 is 30m, ts4 is 1hr, etc.

So in essence the algorithm would be "back filtering", filtering the larger time segment with the smaller time segment.

The main question is how to identify what is noise to apply to the next larger time segment.

### Noise profiling ideas

1) Lets define ts0 as all of the most recent price values in a 1m time interval. One idea is to calculate the average
of ts0 values:
avg0 = AVERAGE(ts0.values)

Now find the standard deviation of ts1.values:
stddev0 = STDDEV(ts0.values)

We can now define noise as any values outside of the range [avg0 - stddev0, avg0 + stddev0] and remove those values
from ts0.

2) Now lets say ts1 is recent price values in 5m time interval, find average of ts1.values:
avg1 = AVERAGE(ts1.values)

Now remove all values from ts1.values that are outside of [avg1 - stddev0, avg1 + stddev0]

Recompute avg1 and compute stddev1:
avg1 = AVERAGE(ts1.values)
stddev1 = STDDEV(ts1.values)

Now remove all values from ts1.values that are outside of [avg1 - stddev1, avg1 + stddev1]

3) Now lets say ts2 is recent price values in 15m time interval, find average of ts2.values:
avg2 = AVERAGE(ts2.values)

Now remove all values from ts1.values that are outside of [avg2 - stddev1, avg2 + stddev1]

Recompute avg2 and compute stddev2:
avg2 = AVERAGE(ts2.values)
stddev2 = STDDEV(ts2.values)

Now remove all values from ts2.values that are outside of [avg2 - stddev2, avg2 + stddev2]

...............

Lets say ts2 is the actual time segment we are interested in. ts2.values has been filtered by the noise profile
from ts0 and ts1. Without using a traditional moving average, we are back filtering to larger and larger time segments,
so in theory the largest time segment will be well filtered from noise, and in effect will have smoothed the largest
time segment.