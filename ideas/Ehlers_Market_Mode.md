## https://www.prorealcode.com/prorealtime-indicators/market-mode/

//PRC_LMarket Mode | indicator
//29.12.2017
//Nicolas @ www.prorealcode.com
//Sharing ProRealTime knowledge
//translated from MQL4 code

MMPeriod = 20 // Market mode period
Delta = 0.5 // Delta
Fraction = 0.8 // Fraction
LevelUpAveragePeriod = 10 // Level up average period
LevelDownAveragePeriod = 10 // Level down average period

Price = (high+low)/2
MPI = 3.14159265358979323846
calc = 2.0*MPI/MMPeriod
beta = cos(calc /(2*MPI)*360)
calc2 = 4.0*MPI*Delta/MMPeriod
gamma   = 1.0 / Cos(calc2 / (4.0*MPI*Delta) *360)

alpha   = gamma - Sqrt(gamma*gamma-1.0)
alphaUp = 2.0 /(1.0+LevelUpAveragePeriod)
alphaDn = 2.0 /(1.0+LevelDownAveragePeriod)
dPeriod = 2*MMPeriod

if barindex>MMPeriod then

 workbp = 0.5*(1.0-alpha)*(price-price[2])+beta*(1.0+alpha)*workbp[1]-alpha*workbp[2]

 mean = workbp

 for k=1 to dPeriod-1 do
  mean = mean+workbp[k]
  inc=k
 next
 mean = mean/inc

 workapeak = workapeak[1]
 if(mean>0) then
  workapeak=workapeak[1]+alphaup*(mean-workapeak[1])
 endif
 workavaley=workavaley[1]
 if(mean<0) then
  workavaley=workavaley[1]+alphadn*(mean-workavaley[1])
 endif

 fractionUp = Fraction*workapeak
 fractionDn = Fraction*workavaley

 r=255
 g=255
 b=255
 if mean>fractionUp then
  r=50
  g=205
  b=50
 elsif mean<fractionDn then
  r=219
  g=112
  b=147
 endif

 if mean crosses over fractionUp then 
  drawtext("●",barindex,mean,Dialog,Bold,16) coloured(0,255,0)
 endif
 if mean crosses under fractionDn then
  drawtext("●",barindex,mean,Dialog,Bold,16) coloured(255,0,0)
 endif
endif

return mean coloured(r,g,b) style(line,2) as "Mean",fractionUp coloured(100,100,100) as "upper line",fractionDn coloured(100,100,100) as "lower line"