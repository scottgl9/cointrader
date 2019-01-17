## http://bettersystemtrader.com/103-a-new-responsive-indicator-with-john-ehlers/
## https://www.prorealcode.com/prorealtime-indicators/john-ehlers-forward-reverse-ema/
AA= 0.1
CC = 1 - AA
if barindex = 1 then
 CC = .9
 RE1 = 0
 RE2 = 0
 RE3 =0
 RE4 = 0
 RE5 = 0
 RE6 = 0
 RE7 = 0
 RE8 = 0
 EMA = 0
 Signal = 0
endif
 
if barindex > 1 then
 EMA = AA*Close + CC*EMA[1]
 
 RE1 = CC*EMA + EMA[1]
 RE2 = EXP(2*LOG(CC))*RE1 + RE1[1]
 RE3 = EXP(4*LOG(CC))*RE2 + RE2[1]
 RE4 = EXP(8*LOG(CC))*RE3 + RE3[1]
 RE5 = EXP(16*LOG(CC))*RE4 + RE4[1]
 RE6 = EXP(32*LOG(CC))*RE5 + RE5[1]
 RE7 = EXP(64*LOG(CC))*RE6 + RE6[1]
 RE8 = EXP(128*LOG(CC))*RE7 + RE7[1]
 Signal = EMA - AA*RE8
endif
 
return Signal,0