## Determining price movement based on ratio of acceleration of two MAs
- For price data that moves with time, define function P(t)
- In physics terms, the velocity is the derivative of P(t) which we'll call V(t), and acceleration is the derivative
  of the velocity which we'll call A(t)
- V(t) = (P(t+1) - P(t)) / (t + 1 - t) = P(t+1) - P(t) for unit time (in this case 1 hour)
- A(t) = (V(t+1) - V(t)) / (t + 1 - t) = V(t+1) - V(t) for unit time (1 hour)

Take two MAs, EMA26 and EMA200 for example. We will calculate the acceleration of EMA26, and acceleration of EMA200.
We'll call A26(t) acceleration of EMA26, an A200(t) acceleration of EMA200.

Relative Acceleration(t) = A26(t) / A200(t)
