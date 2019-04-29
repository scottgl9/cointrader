// https://www.tradingview.com/script/Uyv9vQc2-Williams-Fractals-Tutorial-Template/
// Bill Williams Fractal Template
// Coded By: Matthew Spencer
// If you like this script or use it's code in one of yours, please donate.
// PayPal: ma.spencer@gmx.com Bitcoin: 1foxypuyuoNp5n1LNCCCCmjZ4RAXntQ8X

// Define our title and that this script will overlay the candles.
study("Williams Fractals",shorttitle="Fractals", overlay=true)

// Define "n" as the number of periods and keep a minimum value of 2 for error handling.
n = input(title="Periods", defval=2, minval=2, type=integer)

// Williams Fractals are a 5 point lagging indicator that will draw 2 candles behind.
// The purpose of the indicator is to plot points of trend reversals.
// Often these are paired with trailing stop indicators such as Parabolic SAR, Volatility Stop, and SuperTrend.

// Down pointing fractals occur over candles when:
//   High(n-2) < High(n)
//   High(n-1) < High(n)
//   High(n + 1) < High(n)
//   High(n + 2) < High(n)
dnFractal = (high[n-2] < high[n]) and (high[n-1] < high[n]) and (high[n+1] < high[n]) and (high[n+2] < high[n])

// Up pointing fractals occur under candles when:
//   Low(n-2) > Low(n) 
//   Low(n-1) > Low(n)
//   Low(n + 1) > Low(n) 
//   Low(n + 2) > Low(n)
upFractal = (low[n-2] > low[n]) and (low[n-1] > low[n]) and (low[n+1] > low[n]) and (low[n+2] > low[n])

// Plot the fractals as shapes on the chart.
plotshape(dnFractal, style=shape.arrowdown, location=location.abovebar, offset=-2, color=olive, transp=0) // Down Arrow above candles
plotshape(upFractal, style=shape.arrowup, location=location.belowbar, offset=-2, color=maroon, transp=0)  // Up Arrow below candles

#########################################################################################################################################

// https://www.tradingview.com/script/ZBvF1Vjq-Fractal-Breakout-V2/
//@version=2
study("Fractal Breakout V3", shorttitle="FB", overlay=true)
//tf = input(title="Resolution", type=resolution, defval = "current")
//vamp = input(title="VolumeMA", type=integer, defval=2)
//useVol = input(false,title="Use Volume?")
extremePast_len = input(5,title="# Values to Consider for Pivot Determination, try 5-7")
use_shading = input(true,title="Use shading?")
use_pattern_helpers = input(true,title="Use Pattern Helpers (new dotted lines)?")
use_slope_extensions = input(false,title="Use Slope Extensions (old dotted lines)?")
pattern_slope_tol = input(50.0,title="Slope Tolerance for Line Continuation (x0.01%), try 20-1000")

//vamp_valid = vamp>0?vamp:1
//vam = sma(volume, vamp_valid)

extremePast_len_valid = extremePast_len>1?extremePast_len:2
offset_len = extremePast_len_valid/2 // plot breaks if I take the floor here
offset_len_floor = max(floor(offset_len),1)
minimum_ticks = 50

//up and down are true now, when the extreme occurred offset_len_floor ago. up\down are never true until after 50 ticks
up = n>minimum_ticks?(high[offset_len_floor]>=highest(high,extremePast_len_valid)):false// and (useVol?volume>=vam:true)):false
down = n>minimum_ticks?(low[offset_len_floor]<=lowest(low,extremePast_len_valid)):false// and (useVol?volume>=vam:true)):false
//if an extreme occurred offset_len_floor ago, put it in fractalup\down now, otherwise remember last extreme
fractalup =  up?high[offset_len_floor]:fractalup[1]
fractaldown = down?low[offset_len_floor]:fractaldown[1]

//if an extreme occurred offset_len_floor ago, capture the n value at that time and remember it
nUp = up?n[offset_len_floor]:nz(nUp[1],n)
nDown = down?n[offset_len_floor]:nz(nDown[1],n)
//calculate how many ticks it HAD been, offset_len_floor ago, since last extreme
nUpAgo = n>minimum_ticks?(n[offset_len_floor]-nUp):0
nDownAgo = n>minimum_ticks?(n[offset_len_floor]-nDown):0

//if extreme has occurred offset_len_floor ago, capture that extreme value once.
//////used for (interpolated) trend line plotting
tops = up?fractalup:na
bottoms = down?fractaldown:na

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////resolution basis changes removed for now, as my slope calc can't handle it...please use v1 to retain this feature
//courtesy of synapticex's original fractal line code, for resolution basis changing
//////...modified so these basically mirror tops\bottoms
//ftopstf = security(tickerid,tf == "current" ? period : tf, tops)
//fbottomstf = security(tickerid,tf == "current" ? period : tf, bottoms)
//
//ditto, mirroring the remembered extreme values
//fuptf = security(tickerid,tf == "current" ? period : tf, fractalup)
//fdowntf = security(tickerid,tf == "current" ? period : tf, fractaldown)
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//if an extreme occurred offset_len_floor ago, calculate rise/run
topsSlope = up?((fractalup-fractalup[nUpAgo[1]])/(nUpAgo[1]+1)):0 //nUpAgo will already have the latest extreme's n value
bottomsSlope = down?((fractaldown-fractaldown[nDownAgo[1]])/(nDownAgo[1]+1)):0

//if an extreme occurred offset_len_floor ago, capture the calculated slope, otherwise remember last slope
topsLastSlope = up?(topsSlope):(nz(topsLastSlope[1]))
bottomsLastSlope = down?(bottomsSlope):(nz(bottomsLastSlope[1]))

//if an extreme occurred offset_len_floor ago, start at that extreme, otherwise, increment by slope value
topsExtension = up?fractalup:nz(topsExtension[1],high)+topsLastSlope
bottomsExtension = down?fractaldown:nz(bottomsExtension[1],low)+bottomsLastSlope

//topsPatternSlope = abs(topsLastSlope-nz(topsPatternSlope[1])/nz(topsPatternSlope[1],1))<abs(pattern_slope_tol/100)?nz(topsPatternSlope[1]):topsLastSlope
//bottomsPatternSlope = abs(bottomsLastSlope-nz(bottomsPatternSlope[1])/nz(bottomsPatternSlope[1],1))<abs(pattern_slope_tol/100)?nz(bottomsPatternSlope[1]):bottomsLastSlope

//topsPatternExtension = (topsPatternSlope!=nz(topsPatternSlope[1]))?fractalup:nz(topsPatternExtension[1],high)+topsPatternSlope
//bottomsPatternExtension = (bottomsPatternSlope!=nz(bottomsPatternSlope[1]))?fractaldown:nz(bottomsPatternExtension[1],high)+bottomsPatternSlope

//if an extreme occurred offset_len_floor ago, find difference between new extreme and last ext val, ratio of last ext val
topsPatternDiff = up?(abs(tops-nz(topsPatternExtension[1]))/abs(nz(topsPatternExtension[1],1))):na
bottomsPatternDiff = down?(abs(bottoms-nz(bottomsPatternExtension[1]))/abs(nz(bottomsPatternExtension[1],1))):na
//and compare to tolerance ratio
topsPatternDiffLarge = up?(topsPatternDiff>abs(pattern_slope_tol/10000)):na
bottomsPatternDiffLarge = down?(bottomsPatternDiff>abs(pattern_slope_tol/10000)):na

//if an extreme occurred offset_len_floor ago far from last ext value, reset to new slope, otherwise, remember ext slope
topsPatternSlope = up?(topsPatternDiffLarge?topsSlope:nz(topsPatternSlope[1])):nz(topsPatternSlope[1])
bottomsPatternSlope = down?(bottomsPatternDiffLarge?bottomsSlope:nz(bottomsPatternSlope[1])):nz(bottomsPatternSlope[1])

//increment to next ext val, if needed
topsPatternExtNext = nz(topsPatternExtension[1])+topsPatternSlope
bottomsPatternExtNext = nz(bottomsPatternExtension[1])+bottomsPatternSlope

//if an extreme occurred offset_len_floor ago far from last ext value, reset to new extreme, otherwise, increment last extension val
topsPatternExtension = up?(topsPatternDiffLarge?fractalup:topsPatternExtNext):(topsPatternExtNext)
bottomsPatternExtension = down?(bottomsPatternDiffLarge?fractaldown:bottomsPatternExtNext):(bottomsPatternExtNext)

colorTops = use_slope_extensions?(high[offset_len_floor]>topsExtension?color(#00B200,0):topsExtension<bottomsExtension?color(#00B200,100):color(#00B200,80)):na
colorBottoms = use_slope_extensions?(low[offset_len_floor]<bottomsExtension?color(#B20000,0):bottomsExtension>topsExtension?color(#B20000,100):color(#B20000,80)):na

bouncer = na(tops)?na(bottoms)?na:bottoms:tops

pbounce = plot(bouncer, "Trend", color=blue, linewidth=3, style=line, offset=-offset_len)

ptop = plot(tops, "Fractal Tops", color=lime, linewidth=2, style=line, offset=-offset_len)
pbot = plot(bottoms, "Fractal Tops", color=red, linewidth=2, style=line, offset=-offset_len)

pxt = plot(topsExtension,color=colorTops,linewidth=3,style=circles,offset=-offset_len)
pxb = plot(bottomsExtension,color=colorBottoms,linewidth=3,style=circles,offset=-offset_len)

phigh = plot(high,color=na)
plow = plot(low,color=na)

colorpxt = use_shading?(high[offset_len_floor]>topsPatternExtension?color(#00B200,85):topsPatternExtension<bottomsPatternExtension?color(#00B200,100):color(#B20000,100)):color(#000000,100)
colorpxb = use_shading?(low[offset_len_floor]<bottomsPatternExtension?color(#B20000,75):bottomsPatternExtension>topsPatternExtension?color(#B20000,100):color(#00B200,100)):color(#000000,100)

colorppt = use_pattern_helpers?(high[offset_len_floor]>topsPatternExtension?color(#00FF00,0):topsPatternExtension<bottomsPatternExtension?color(#00FF00,90):color(#00FF00,0)):color(#000000,100)
colorppb = use_pattern_helpers?(low[offset_len_floor]<bottomsPatternExtension?color(#FF0000,0):topsPatternExtension<bottomsPatternExtension?color(#FF0000,90):color(#FF0000,0)):color(#000000,100)

pxtPatt = plot(topsPatternExtension,color=colorppt,style=circles,linewidth=2,offset=-offset_len)
pxbPatt = plot(bottomsPatternExtension,color=colorppb,style=circles,linewidth=2,offset=-offset_len)

fill(pxtPatt,phigh,color=colorpxt)
fill(pxbPatt,plow,color=colorpxb)

// alertcondition(up or down,"Bounce","Fractal extreme detected")
// alertcondition((down or down[1]) and high[offset_len_floor]>high[offset_len_floor+1] 
//   and (open[offset_len_floor+1]>close[offset_len_floor+1])
//   and (high[offset_len_floor+1]-open[offset_len_floor+1])<(open[offset_len_floor+1]-close[offset_len_floor+1])*0.2 
//   and (close[offset_len_floor+1]-low[offset_len_floor+1])<(open[offset_len_floor+1]-close[offset_len_floor+1])*0.2 
//   and (open[offset_len_floor]<close[offset_len_floor])
//   and (high[offset_len_floor]-open[offset_len_floor])<(open[offset_len_floor]-close[offset_len_floor])*0.2 
//   and (close[offset_len_floor]-low[offset_len_floor])<(open[offset_len_floor]-close[offset_len_floor])*0.2 
//   ,"PiercingLine","Possible piercing line detected")


//plot(fuptf, "FractalUp", color=lime, linewidth=1, style=cross, transp=70, offset =-offset_len, join=false)
//plot(fdowntf, "FractalDown", color=red, linewidth=1, style=cross, transp=70, offset=-offset_len, join=false)