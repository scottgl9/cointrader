//https://www.prorealcode.com/prorealtime-indicators/variable-moving-average-vma/
//PRC_Variable Moving Average | indicator
//14.12.2016
//Nicolas @ www.prorealcode.com
//Sharing ProRealTime knowledge
//converted and adapted from Pinescript version
 
// --- parameters
src=customclose
//l = 6
 
if barindex>l then
 k = 1.0/l
 pdm = max((src - src[1]), 0)
 mdm = max((src[1] - src), 0)
 pdmS = ((1 - k)*(pdmS[1]) + k*pdm)
 mdmS = ((1 - k)*(mdmS[1]) + k*mdm)
 s = pdmS + mdmS
 pdi = pdmS/s
 mdi = mdmS/s
 pdiS = ((1 - k)*(pdiS[1]) + k*pdi)
 mdiS = ((1 - k)*(mdiS[1]) + k*mdi)
 d = abs(pdiS - mdiS)
 s1 = pdiS + mdiS
 iS = ((1 - k)*(iS[1]) + k*d/s1)
 hhv = highest[l](iS)
 llv = lowest[l](iS)
 d1 = hhv - llv
 vI = (iS - llv)/d1
 vma = (1 - k*vI)*(vma[1]) + k*vI*src
endif
 
RETURN VMA