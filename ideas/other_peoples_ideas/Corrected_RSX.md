//PRC_Corrected RSX | indicator
//21.09.2018
//Nicolas @ www.prorealcode.com
//Sharing ProRealTime knowledge
//converted from MT5 version (mladen)

// --- settings
RSIperiod = 14
// --- end of settings

rsiprice=customclose

//RSX
Len=rsiperiod
smallRsiValue = 0.0000000000000001
if (f90 = 0.0) then
 f90 = 1.0
 f0 = 0.0
 if (Len-1 >= 5) then
  f88 = Len-1.0
 else
  f88 = 5.0
 endif
 f8 = 100.0*(rsiprice)
 f18 = 3.0 / (Len + 2.0)
 f20 = 1.0 - f18
else
 if (f88 <= f90) then
  f90 = f88 + 1
 else
  f90 = f90 + 1
 endif
 f10 = f8
 f8 = 100*Close
 v8 = f8 - f10
 f28 = f20 * f28 + f18 * v8
 f30 = f18 * f28 + f20 * f30
 vC = f28 * 1.5 - f30 * 0.5
 f38 = f20 * f38 + f18 * vC
 f40 = f18 * f38 + f20 * f40
 v10 = f38 * 1.5 - f40 * 0.5
 f48 = f20 * f48 + f18 * v10
 f50 = f18 * f48 + f20 * f50
 v14 = f48 * 1.5 - f50 * 0.5
 f58 = f20 * f58 + f18 * Abs(v8)
 f60 = f18 * f58 + f20 * f60
 v18 = f58 * 1.5 - f60 * 0.5
 f68 = f20 * f68 + f18 * v18

 f70 = f18 * f68 + f20 * f70
 v1C = f68 * 1.5 - f70 * 0.5
 f78 = f20 * f78 + f18 * v1C
 f80 = f18 * f78 + f20 * f80
 v20 = f78 * 1.5 - f80 * 0.5

 if ((f88 >= f90) and (f8 <> f10)) then
  f0 = 1.0
 endif
 if ((f88 = f90) and (f0 = 0.0)) then
  f90 = 0.0
 endif
endif


if ((f88 < f90) and (v20 > smallRsiValue)) then

 v4 = (v14 / v20 + 1.0) * 50.0
 if (v4 > 100.0) then
  v4 = 100.0
 endif
 if (v4 < 0.0) then
  v4 = 0.0
 endif
else
 v4 = 50.0
endif

irsi=v4

//Corrected function
if barindex>RSIperiod then
 n=RSIperiod
 SA = irsi
 v1 = SQUARE(STD[n](SA))
 v2 = SQUARE(CA[1]-SA)
 if(v2<v1) then
  k=0
 else
  k=1-v1/v2
  CA=CA[1]+K*(SA-CA[1])
 endif
endif

//final cut
if CA>CA[1] then
 r=0
 g=191
 b=255
elsif CA<CA[1] then
 r=244
 g=164
 b=96
endif

return irsi coloured(r,g,b) style(dottedline,2) as "RSX", CA coloured(r,g,b) style(line,3) as "Corrected RSX"