https://www.prorealcode.com/prorealtime-indicators/john-ehlers-mama-the-mother-of-adaptive-moving-average/
//parameters :
// FastLimit = 0.5
// SlowLimit = 0.05

Price = (High+Low)/2

if(barindex>5) then
Smooth = (4*Price + 3*Price[1] + 2*Price[2] + Price[3]) / 10
Detrender = (.0962*Smooth + .5769*Smooth[2] - .5769*Smooth[4] - .0962*Smooth[6])*(.075*Period[1] + .54)

Q1 = (.0962*Detrender + .5769*Detrender[2] - .5769*Detrender[4] - .0962*Detrender[6])*(.075*Period[1] + .54)
I1 = Detrender[3]

jI = (.0962*I1 + .5769*I1[2] - .5769*I1[4] - .0962*I1[6])*(.075*Period[1] + .54)
jQ = (.0962*Q1 + .5769*Q1[2] - .5769*Q1[4] - .0962*Q1[6])*(.075*Period[1] + .54)

I2 = I1 - jQ
Q2 = Q1 + jI

I2 = .2*I2 + .8*I2[1]
Q2 = .2*Q2 + .8*Q2[1]

Re = I2*I2[1] + Q2*Q2[1]
Im = I2*Q2[1] - Q2*I2[1]
Re = .2*Re + .8*Re[1]
Im = .2*Im + .8*Im[1]
If Im <> 0 and Re <> 0 then
Period = 360/ATAN(Im/Re)
endif
If Period > 1.5*Period[1] then
Period = 1.5*Period[1]
endif
If Period < .67*Period[1] then
Period = .67*Period[1]
endif
If Period < 6 then
Period = 6
endif
If Period > 50 then
Period = 50
endif

Period = .2*Period + .8*Period[1]
SmoothPeriod = .33*Period + .67*SmoothPeriod[1]

if(I1<>0) then
Phase = ATAN(Q1 / I1)
endif

DeltaPhase = Phase[1] - Phase
If DeltaPhase < 1 then
DeltaPhase = 1
endif

alpha = FastLimit / DeltaPhase
If alpha < SlowLimit then
alpha = SlowLimit
endif

MAMA = alpha*Price + (1 - alpha)*MAMA[1]
FAMA = .5*alpha*MAMA + (1 - .5*alpha)*FAMA[1]

endif

RETURN MAMA as "MAMA", FAMA as "FAMA"


iff() - iff(if, then, else)

//
// @author LazyBear 
// 
// List of my public indicators: http://bit.ly/1LQaPK8 
// List of my app-store indicators: http://blog.tradingview.com/?p=970 
//
study("Ehlers MESA Adaptive Moving Average [LazyBear]", shorttitle="EMAMA_LB", overlay=true, precision=3)
src=input(hl2, title="Source")
fl=input(.5, title="Fast Limit")
sl=input(.05, title="Slow Limit")
sp = (4*src + 3*src[1] + 2*src[2] + src[3]) / 10.0
dt = (.0962*sp + .5769*nz(sp[2]) - .5769*nz(sp[4])- .0962*nz(sp[6]))*(.075*nz(p[1]) + .54)
q1 = (.0962*dt + .5769*nz(dt[2]) - .5769*nz(dt[4])- .0962*nz(dt[6]))*(.075*nz(p[1]) + .54)
i1 = nz(dt[3])
jI = (.0962*i1 + .5769*nz(i1[2]) - .5769*nz(i1[4])- .0962*nz(i1[6]))*(.075*nz(p[1]) + .54)
jq = (.0962*q1 + .5769*nz(q1[2]) - .5769*nz(q1[4])- .0962*nz(q1[6]))*(.075*nz(p[1]) + .54)
i2_ = i1 - jq
q2_ = q1 + jI
i2 = .2*i2_ + .8*nz(i2[1])
q2 = .2*q2_ + .8*nz(q2[1])
re_ = i2*nz(i2[1]) + q2*nz(q2[1])
im_ = i2*nz(q2[1]) - q2*nz(i2[1])
re = .2*re_ + .8*nz(re[1])
im = .2*im_ + .8*nz(im[1])
p1 = iff(im!=0 and re!=0, 360/atan(im/re), nz(p[1]))
p2 = iff(p1 > 1.5*nz(p1[1]), 1.5*nz(p1[1]), iff(p1 < 0.67*nz(p1[1]), 0.67*nz(p1[1]), p1))
p3 = iff(p2<6, 6, iff (p2 > 50, 50, p2))
p = .2*p3 + .8*nz(p3[1])
spp = .33*p + .67*nz(spp[1])
phase = atan(q1 / i1)
dphase_ = nz(phase[1]) - phase
dphase = iff(dphase_< 1, 1, dphase_)
alpha_ = fl / dphase
alpha = iff(alpha_ < sl, sl, iff(alpha_ > fl, fl, alpha_))
mama = alpha*src + (1 - alpha)*nz(mama[1])
fama = .5*alpha*mama + (1 - .5*alpha)*nz(fama[1])
pa=input(false, title="Mark crossover points")
plotarrow(pa?(cross(mama, fama)?mama<fama?-1:1:na):na, title="Crossover Markers")
fr=input(false, title="Fill MAMA/FAMA Region")
duml=plot(fr?(mama>fama?mama:fama):na, style=circles, color=gray, linewidth=0, title="DummyL")
mamal=plot(mama, title="MAMA", color=red, linewidth=2)
famal=plot(fama, title="FAMA", color=green, linewidth=2)
fill(duml, mamal, red, transp=70, title="NegativeFill")
fill(duml, famal, green, transp=70, title="PositiveFill")
ebc=input(false, title="Enable Bar colors")
bc=mama>fama?lime:red
barcolor(ebc?bc:na)


(for weird reasons paste operation sometimes posts my comment :) ) 

wrong: 
p1 = iff(im!=0 and re!=0, 360/atan(im/re), nz(p)) 

right: 
p1 = iff(im!=0 and re!=0, 2*pi/atan(im/re), nz(p)), where pi = 3.14.5926 

Phase, line 30 
wrong: 
phase = atan(q1 / i1) 

right: 
phase = 180/pi * atan(q1 / i1) 

line 21: 
p1 = iff(im!=0 and re!=0, 2*pi/atan(im/re), nz(p)) 

line 30 (old count again): 
phase = 180/pi * atan(q1 / i1) 