## https://www.prorealcode.com/prorealtime-indicators/recursive-median-oscillator-john-ehlers/

LPPeriod=12
HPPeriod=30
length=5
once Median=0
if barindex>length then
 // Set EMA constant from LPPeriod input
 Alpha1 = ( Cos( 360 / LPPeriod )+ Sin( 360 / LPPeriod ) - 1 )/ Cos( 360 / LPPeriod )

 // get the median of the last length (default=5) closes

 FOR X = 0 TO length-1
  M = close[X]    //this example takes the median of the last 5 closes
  SmallPart = 0
  LargePart = 0
  FOR Y = 0 TO length-1
   IF close[Y] < M THEN
    SmallPart = SmallPart + 1
   ELSIF close[Y] > M THEN
    LargePart = LargePart + 1
   ENDIF
   IF LargePart = SmallPart AND Y = length-1 THEN
    Median = M
    BREAK
   ENDIF
  NEXT
 NEXT

 // Recursive Median (EMA of a 5
 // bar Median filter)

 RM = Alpha1 * Median + ( 1 - Alpha1 ) * RM[1]

 // Highpass filter cyclic components
 // whose periods are shorter than
 // HPPeriod to make an oscillator

 Alpha2 = ( Cos( .707 * 360 / HPPeriod ) + Sin( .707 * 360 / HPPeriod ) - 1 ) / Cos( .707 * 360 / HPPeriod )

 RMO = ( 1 - Alpha2 / 2 ) * ( 1 - Alpha2 / 2 ) * ( RM - 2 * RM[1] + RM[2] ) + 2 * ( 1 - Alpha2 ) * RMO[1] - ( 1 - Alpha2 ) * ( 1 - Alpha2 ) * RMO[2]
endif

return RMO as "RMO", 0 as "0"