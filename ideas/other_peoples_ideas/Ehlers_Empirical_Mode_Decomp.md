## https://www.prorealcode.com/prorealtime-indicators/john-ehlers-empirical-mode-decomposition/

//PRC_EmpiricalModeDecomposition | indicator
//20.02.2017
//Nicolas @ www.prorealcode.com
//Sharing ProRealTime knowledge
//converted from EasyLanguage code
 
//--- parameters
// Period=20
// delta=.1
// Fraction=.25
// ---
 
Price = medianprice
 
if barindex>Period then
 beta = Cos(360 / Period)
 gamma = 1 / Cos(720*delta / Period)
 alpha = gamma - SqRt(gamma*gamma - 1)
 BP = .5*(1 - alpha)*(Price - Price[2]) + beta*(1 + alpha)*BP[1] - alpha*BP[2]
 Mean = Average[Period*2](BP)
 Peak = Peak[1]
 Valley = Valley[1]
 If BP[1] > BP and BP[1] > BP[2] Then
  Peak = BP[1]
 endif
 If BP[1] < BP and BP[1] < BP[2] Then
  Valley = BP[1]
 endif
 AvgPeak = Average[50](Peak)
 AvgValley = Average[50](Valley)
endif
 
return Mean as "mean", Fraction*AvgPeak as "avg peak", Fraction*AvgValley as "avg valley"
 