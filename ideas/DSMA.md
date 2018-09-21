## https://www.prorealcode.com/prorealtime-indicators/deviation-scaled-moving-average-dsma/

//PRC_Deviation Scaled Moving Average | indicator
//15.06.2018
//Nicolas @ www.prorealcode.com
//Sharing ProRealTime knowledge
 
// --- settings
Period = 40
// --- end of settings
 
If barindex>Period Then
 //Smooth with a Super Smoother
 a1 = exp(-1.414*3.14159 / (.5*Period))
 b1 = 2*a1*Cos(1.414*180 / (.5*Period))
 c2 = b1
 c3 = -a1*a1
 c1 = 1 - c2 - c3
 //Produce Nominal zero mean with zeros in the transfer response
 //at DC and Nyquist with no spectral distortion
 //Nominally whitens the spectrum because of 6 dB per octave
 //rolloff
 Zeros = Close - Close[2]
 //SuperSmoother Filter
 Filt = c1*(Zeros + Zeros[1]) / 2 + c2*Filt[1] + c3*Filt[2]
 //Compute Standard Deviation
 RMS = 0
 For count = 0 to Period - 1 do
  RMS = RMS + Filt[count]*Filt[count]
 next
 RMS = SqRt(RMS / Period)
 //Rescale Filt in terms of Standard Deviations
 ScaledFilt = Filt / RMS
 alpha1 = Abs(ScaledFilt)*5 / Period
 DSMA = alpha1*Close + (1 - alpha1)*DSMA[1]
endif
 
return DSMA