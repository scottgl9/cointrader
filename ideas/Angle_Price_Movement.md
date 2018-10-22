### Angle of Price Movement

In order to determine the angle of price movement, need to select a timeframe from t1 to t2. Frome this timeframe,
we then need to create a virtual box. The reason is that a calculate of angle from a ratio needs to be a unit-less
calculation. In other words, need a way to convert time and price to both unit-less quantities, so that we are able
to calculate a ratio, and therefore deriving the angle from that ratio.

From plotting price vs time it's easy to see what the approximate angle should be, but this can be very difficult
to calculate since angle is relative to perception. 

One possible way of calculating the angle of the slope is from calculating the angle between two vectors:
cos(theta) = (vector_u . vector_v) / (magnitude(vector_u) . magnitude(vector_v)) where '.' denotes a dot product

#### The primary problem remains relating units of time to units of price

In order to put price and time on the same scale, we need to determine the maximum possible price movement for a given
timeframe. Also the timeframe needs to be uniform time increments (ex. 1s, 1m, 5m, etc.).

We want to limit the angle of the slope to -90 < angle_slope < 90. So lets say the absolute maximum angle we will
allow is 80 degrees. So -80 < arctan(delta_price / delta_time) < 80.
If delta_price < 0: -80 < arctan(abs(delta_price) / delta_time) < 0
If delta_price > 0: 80 > arctan(abs(delta_price) / delta_time) > 0

80 = arctan(abs(max_delta_price) / delta_time)
tan(80) = abs(max_delta_price) / delta_time
abs(max_delta_price) = delta_time * tan(80) 

So the maximum delta_price for a given timeframe is:
abs(max_delta_price) = delta_time * tan(80)

The problem with the above is it's not unit-less. Could possibly designate time as number of timeframes, and
price as ratio of price_frames / max_price_frames