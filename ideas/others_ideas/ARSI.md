## https://www.prorealcode.com/prorealtime-indicators/john-ehlers-adaptive-rsi/

// Adaptive Relative Strength Index (RSI)
// Rocket Science for Traders: Digital Signal Processing Applications
// 2001-07-20 John F. Ehlers

Price = (high+low)/2
CycPart = .5

If BarIndex > 5 then
	Smooth = (4*Price + 3*Price[1] + 2*Price[2] + Price[3]) / 10
	Detrender = (.0962*Smooth + .5769*Smooth[2] - .5769*Smooth[4] - .0962*Smooth[6])*(.075*Period[1] + .54)

	// Compute InPhase and Quadrature components
	Q1 = (.0962*Detrender + .5769*Detrender[2] - .5769*Detrender[4] - .0962*Detrender[6])*(.075*Period[1] + .54)
	I1 = Detrender[3]

	// Advance the phase of I1 and Q1 by 90 degrees
	j1 = (.0962*I1 + .5769*I1[2] - .5769*I1[4] - .0962*I1[6])*(.075*Period[1] + .54)
	jQ = (.0962*Q1 + .5769*Q1[2] - .5769*Q1[4] - .0962*Q1[6])*(.075*Period[1] + .54)

	// Phasor addition for 3 bar averaging
	I2 = I1 - jQ
	Q2 = Q1 + j1

	// Smooth the I and Q components before applying the discriminator
	I2 = .2*I2 + .8*I2[1]
	Q2 = .2*Q2 + .8*Q2[1]

	// Homodyne Discriminator
	Re = I2*I2[1] + Q2*Q2[1]
	Im = I2*Q2[1] - Q2*I2[1]
	Re = .2*Re + .8*Re[1]
	Im = .2*Im + .8*Im[1]
	If Im <> 0 and Re <> 0 then
		Period = 360/ATAN(Im/Re)
	Endif
	If Period > 1.5*Period[1] then
		Period = 1.5*Period[1]
	Endif
	If Period < .67*Period[1] then
		Period = .67*Period[1]
	Endif
	If Period < 6 then
		Period = 6
	Endif
	If Period > 50 then
		Period = 50
	Endif
	Period = .2*Period + .8*Period[1]
	SmoothPeriod = .33*Period + .67*SmoothPeriod[1]

	CU = 0
	CD = 0
	For count = 0 to ROUND(CycPart*SmoothPeriod) - 1 do
		If Close[count] - Close[count + 1] > 0 then
			CU = CU + (Close[count] - Close[count + 1])
		Endif
		If Close[count] - Close[count + 1] < 0 then
			CD = CD + (Close[count + 1] - Close[count])
		Endif
	Next
	If CU + CD <> 0 then
		ARSI = 100*CU / (CU + CD)
	Endif
Endif

Return ARSI as "RSI"