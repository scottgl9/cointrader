## https://www.prorealcode.com/prorealtime-indicators/triple-raff-channel-projection-on-price/

// Triple RAF Channel (Bianca) indicator for PRT
// Written by "Maz" at prorealcode.com
// Adopted from RAFF algorithm
// --

for i = 1 to 3

// Blue (Long term)
if i = 1 then
k   = blue
det = DPO[k*2](close)
if det=det[1] and det[1]=det[2] and det[2]<>det[3] then
flag = 1
endif
n      = (k*2)-4
p      = (n/2)-1
d100   = DPO[n](close)
moy100 = close-d100
co     = (moy100-moy100[1]+(close[p])/n)*n
h100   = dpo[n](high)
moyh   = high-h100
hi     = (moyh-moyh[1]+(high[p])/n)*n
l100   = dpo[n](low)
moyl   = low-l100
lo     = (moyl-moyl[1]+(low[p])/n)*n
if flag=1 and flag[1]=0 then
somx  = 0
somy  = 0
somxx = 0
somxy = 0
for i=1 to k
somx = somx+i
next
for i=0 to k-1
somy=somy+co[i]
next
for i=1 to k
somxx=somxx+(i*i)
next
for i=0 to k-1
somxy=somxy+(co[i]*(k-i))
next
a = (k*somxy-somx*somy)/(k*somxx-somx*somx)
b = (somy-a*somx)/k
for i=0 to k-1
ecah = hi[i]-a*(k-i)-b
maxh = max(maxh,ecah)
ecal = a*(k-i)+b-lo[i]
maxl = max(maxl,ecal)
next
endif
if flag=0 then
reg = undefined
else
j = j + 1
reg = a * j + b
endif

raffBlue  = max(maxh,maxl)
rafflBlue = reg-raffBlue
raffhBlue = reg+raffBlue

riffBlue  = min(maxh,maxl)
riffhBlue = reg+riffBlue
rifflBlue = reg-riffBlue

// (optional) - let's take an average of the riff and raff
BlueResistance = (raffhBlue + riffhBlue) / 2
BlueSupport    = (rafflBlue + rifflBlue) / 2


elsif i = 2 then // Green (Medium term)
k = green
Gdet = DPO[k*2](close)
if Gdet = Gdet[1] and Gdet[1] = Gdet[2] and Gdet[2] <> Gdet[3] then
Gflag = 1
endif
Gn      = (k*2)-4
Gp      = (Gn/2)-1
Gd100   = DPO[Gn](close)
Gmoy100 = close-Gd100
Gco     = (Gmoy100 - Gmoy100[1]+(close[Gp])/Gn)*Gn
Gh100   = dpo[Gn](high)
Gmoyh   = high-Gh100
Ghi     = (Gmoyh - Gmoyh[1]+(high[Gp])/Gn)*Gn
Gl100   = dpo[Gn](low)
Gmoyl   = low-Gl100
Glo     = (Gmoyl-Gmoyl[1]+(low[Gp])/Gn)*Gn
if Gflag = 1 and Gflag[1] = 0 then
Gsomx  = 0
Gsomy  = 0
Gsomxx = 0
Gsomxy = 0
for i = 1 to k
Gsomx = Gsomx+i
next
for i = 0 to k-1
Gsomy=Gsomy+Gco[i]
next
for i = 1 to k
Gsomxx=Gsomxx+(i*i)
next
for i = 0 to k-1
Gsomxy=Gsomxy+(Gco[i]*(k-i))
next
Ga = (k*Gsomxy-Gsomx*Gsomy)/(k*Gsomxx-Gsomx*Gsomx)
Gb = (Gsomy-Ga*Gsomx)/k
for i=0 to k-1
Gecah = Ghi[i]-Ga*(k-i)-Gb
Gmaxh = max(Gmaxh,Gecah)
Gecal = Ga*(k-i)+Gb-Glo[i]
Gmaxl = max(Gmaxl,Gecal)
next
endif
if Gflag = 0 then
Greg = undefined
else
Gj = Gj + 1
Greg = Ga * Gj + Gb
endif

raffGreen  = max(Gmaxh,Gmaxl)
rafflGreen = Greg-raffGreen
raffhGreen = Greg+raffGreen

riffGreen  = min(Gmaxh,Gmaxl)
riffhGreen = Greg+riffGreen
rifflGreen = Greg-riffGreen

// (optional) - let's take an average of the riff and raff
GreenResistance = (raffhGreen + riffhGreen) / 2
GreenSupport    = (rafflGreen + rifflGreen) / 2

elsif i = 3 then // Red (Short Term)
k = red
Rdet = DPO[k*2](close)
if Rdet = Rdet[1] and Rdet[1] = Rdet[2] and Rdet[2] <> Rdet[3] then
Rflag = 1
endif
Rn      = (k*2)-4
Rp      = (Rn/2)-1
Rd100   = DPO[Rn](close)
Rmoy100 = close-Rd100
Rco     = (Rmoy100 - Rmoy100[1]+(close[Rp])/Rn)*Rn
Rh100   = dpo[Rn](high)
Rmoyh   = high-Rh100
Rhi     = (Rmoyh - Rmoyh[1]+(high[Rp])/Rn)*Rn
Rl100   = dpo[Rn](low)
Rmoyl   = low-Rl100
Rlo     = (Rmoyl-Rmoyl[1]+(low[Rp])/Rn)*Rn
if Rflag = 1 and Rflag[1] = 0 then
Rsomx  = 0
Rsomy  = 0
Rsomxx = 0
Rsomxy = 0
for i = 1 to k
Rsomx = Rsomx+i
next
for i = 0 to k-1
Rsomy=Rsomy+Rco[i]
next
for i = 1 to k
Rsomxx=Rsomxx+(i*i)
next
for i = 0 to k-1
Rsomxy=Rsomxy+(Rco[i]*(k-i))
next
Ra = (k*Rsomxy-Rsomx*Rsomy)/(k*Rsomxx-Rsomx*Rsomx)
Rb = (Rsomy-Ra*Rsomx)/k
for i=0 to k-1
Recah = Rhi[i]-Ra*(k-i)-Rb
Rmaxh = max(Rmaxh,Recah)
Recal = Ra*(k-i)+Rb-Rlo[i]
Rmaxl = max(Rmaxl,Recal)
next
endif
if Rflag = 0 then
Rreg = undefined
else
Rj = Rj + 1
Rreg = Ra * Rj + Rb
endif

raffRed  = max(Rmaxh,Rmaxl)
rafflRed = Rreg-raffRed
raffhRed = Rreg+raffRed

riffRed  = min(Rmaxh,Rmaxl)
riffhRed = Rreg+riffRed
rifflRed = Rreg-riffRed

// (optional) - let's take an average of the riff and raff
RedResistance = (raffhRed + riffhRed) / 2
RedSupport    = (rafflRed + rifflRed) / 2
endif

next


return BlueSupport coloured (10, 10, 200) as "Blue Support", BlueResistance coloured (10, 10, 255) as "Blue Resistance" , GreenSupport coloured (10, 200, 10) as "Green Support", GreenResistance coloured (10, 255, 10) as "Green Resistance", RedSupport coloured (200, 10, 10) as "Red Support", RedResistance coloured (255, 10, 10) as "Red Resistance"
