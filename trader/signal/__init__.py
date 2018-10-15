from trader.signal.Bollinger_Bands_Signal import Bollinger_Bands_Signal
from trader.signal.long.Currency_Long_EMA import Currency_EMA_Long
from trader.signal.EFI_Breakout_Signal import EFI_Breakout_Signal
from trader.signal.EMA_OBV_Crossover import EMA_OBV_Crossover
from trader.signal.Hybrid_Crossover import Hybrid_Crossover
from trader.signal.Hybrid2_Crossover import Hybrid2_Crossover
from trader.signal.KST_Crossover import KST_Crossover
from trader.signal.MACD_Crossover import MACD_Crossover
from trader.signal.OBV_Crossover import OBV_Crossover
from trader.signal.PPO_OBV import PPO_OBV
from trader.signal.price_channel_signal import price_channel_signal
from trader.signal.PMO_Crossover import PMO_Crossover
from trader.signal.RSI_OBV import RSI_OBV
from trader.signal.SignalHandler import SignalHandler
from trader.signal.SigType import SigType
from trader.signal.sustained_volume_spike_signal import sustained_volume_spike_signal
from trader.signal.TD_Sequential_Signal import TD_Sequential_Signal
from trader.signal.TSI_Signal import TSI_Signal

def select_signal_name(name):
    if name =="Bollinger_Bands_Signal": return Bollinger_Bands_Signal()
    elif name == "Currency_Long_EMA": return Currency_EMA_Long()
    elif name == "EFI_Breakout_Signal": return EFI_Breakout_Signal()
    elif name == "EMA_OBV_Crossover": return EMA_OBV_Crossover()
    elif name == "Hybrid_Crossover": return Hybrid_Crossover()
    elif name == "Hybrid2_Crossover": return Hybrid2_Crossover()
    elif name == "KST_Crossover": return KST_Crossover()
    elif name == "MACD_Crossover": return MACD_Crossover()
    elif name == "OBV_Crossover": return OBV_Crossover()
    elif name == "PPO_OBV": return PPO_OBV()
    elif name == "price_channel_signal": return price_channel_signal()
    elif name == "PMO_Crossover": return PMO_Crossover()
    elif name == "RSI_OBV": return RSI_OBV()
    elif name == "sustained_volume_spike_signal": return sustained_volume_spike_signal()
    elif name == "TD_Sequential_Signal": return TD_Sequential_Signal()
    elif name == "TSI_Signal": return TSI_Signal()
    return None
