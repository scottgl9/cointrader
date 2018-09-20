## Moving averages to research:

ALMA: Arnaud Legoux Moving Average
AMA: Ahrens Moving Average
Better EMA
FAMA: Fractal Adaptive Moving Average
Harmonic Mean: Moving Average
Holt EMA: Moving Average

McGinley Dynamic:
MD = MD-1 + (Index – MD-1) / (N * (Index / MD-1 ) 4)

MWDX: Moving Average
Percentage Trend Moving Average
PPA: Pivot Point Average
VIDYA: Variable Index Dynamic Average
Wilders: Welles Wilder’s Moving Average

BOP: Balance of Power Oscillator

MDI: Market Direction Indicator (anticipates moving average crossovers):
    calc_cp2(src, len1, len2) =>
        (len1*(sum(src, len2-1)) - len2*(sum(src, len1-1))) / (len2-len1)

    src=close
    lenMA1=input(13, title="Short Length"), lenMA2=input(55, title="Long Length")
    cp2=calc_cp2(src, lenMA1, lenMA2)
    mdi=100*(nz(cp2[1]) - cp2)/((src+src[1])/2)
    mdic=mdi<-cutoff?(mdi<mdi[1]?red:orange):mdi>cutoff?(mdi>mdi[1]?green:lime):gray
