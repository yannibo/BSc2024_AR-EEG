import random
import Levenshtein as lev
import matplotlib.pyplot as plt
import matplotlib
import time


#matplotlib.use('TkAgg')

class DefinedElectrode:
    def __init__(self, name, color, distToFace, neighbors):
        self.name = name
        self.color = color
        self.distToFace = distToFace
        self.neighbors = neighbors
        self.sequence = None


"""
definedElectrodes = [
    DefinedElectrode("FP1", "P", ["AFP3H", "FPZ"]),
    DefinedElectrode("FPZ", "P", ["AFP4H", "FP1", "AFP3H"]),
    DefinedElectrode("FP2", "P", ["AF4", "AF8", "AFP4H"]),
    DefinedElectrode("AFP3H", "Y", ["AFZ", "AFP4H", "FPZ", "FP1"]),
    DefinedElectrode("AFP4H", "Y", ["AF4", "FP2", "FPZ", "AFP3H", "AFZ"]),
    DefinedElectrode("AF7", "G", ["F5", "AFF5H", "F7"]),
    DefinedElectrode("AF3", "G", ["F1", "AFF1", "AFF5H", "F3"]),
    DefinedElectrode("AFZ", "X", ["FZ", "AFF2", "AFP4H", "AFP3H", "AFF1"]),
    DefinedElectrode("AF4", "G", ["F4", "AFF6H", "FP2", "AFP4H", "AFF2", "F2"]),
    DefinedElectrode("AF8", "G", ["F8", "FP2", "AFF6H"]),
    DefinedElectrode("AFF5H", "Y", ["F3", "AF3", "AF7", "F5", "FFC5H"]),
    DefinedElectrode("AFF1", "X", ["FFC1H", "FZ", "AFF2", "AFZ", "AF3", "F1"]),
    DefinedElectrode("AFF2", "X", ["FFC2H", "F2", "AF4", "AFZ", "AFF1", "FZ"]),
    DefinedElectrode("AFF6H", "Y", ["FFC6H", "F6", "F8", "AF8", "AF4", "F4"]),
    DefinedElectrode("F7", "P", ["FFT7H", "F5", "AF7"]),
    DefinedElectrode("F5", "G", ["FFC5H", "F3", "AFF5H", "AF7", "F7", "FFT7H", "FC5"]),
    DefinedElectrode("F3", "P", ["FFC3H", "F1", "AF3", "AFF5H", "F5", "FFC5H", "FC3"]),
    DefinedElectrode("F1", "G", ["FC1", "FFC1H", "FZ", "AFF1", "AF3", "F3", "FFC3H"]),
    DefinedElectrode("FZ", "P", ["FCZ", "FFC2H", "F2", "AFF2", "AFZ", "AFF1", "F1", "FFC1H"]),
    DefinedElectrode("F2", "G", ["FC2", "FFC4H", "F4", "AF4", "AFF2", "FZ", "FFC2H"]),
    DefinedElectrode("F4", "P", ["FC4", "FFC6H", "F6", "AFF6H", "AF4", "F2", "FC2", "FFC4H"]),
    DefinedElectrode("F6", "G", ["FC6", "FFT8H", "F8", "AFF6H", "F4", "FFC6H"]),
    DefinedElectrode("F8", "P", ["FFT8H", "FT8", "AF8", "AFF6H", "F6"]),
    DefinedElectrode("FFT7H", "Y", ["FC5", "FFC5H", "F5", "F7", "FT7"]),
    DefinedElectrode("FFC5H", "X", ["FC3", "FFC3H", "F3", "AFF5H", "F5", "FFT7H", "FC5", "FCC5H"]),
    DefinedElectrode("FFC3H", "X", ["FCC3H", "FC1", "FFC1H", "F1", "F3", "FFC5H", "FC3"]),
    DefinedElectrode("FFC1H", "Y", ["FCC1H", "FCZ", "FFC2H", "FZ", "AFF1", "F1", "FFC3H", "FC1"]),
    DefinedElectrode("FFC2H", "Y", ["FCC2H", "FC2", "FFC4H", "F2", "AFF2", "FZ", "FFC1H", "FCZ"]),
    DefinedElectrode("FFC4H", "X", ["FCC4H", "FC4", "FFC6H", "F4", "F2", "FFC2H", "FC2"]),
    DefinedElectrode("FFC6H", "X", ["FCC6H", "FC6", "F6", "AFF6H", "F4", "FFC4H", "FC4"]),
    DefinedElectrode("FFT8H", "Y", ["FTT8H", "FT8", "F8", "F6", "FC6"]),
    DefinedElectrode("FT9", "X", ["FTT9H"]),
    DefinedElectrode("FT7", "G", ["FTT7H", "FC5", "FFT7H", "FTT9H", "T7"]),
    DefinedElectrode("FC5", "P", ["C5", "FCC5H", "FC3", "FFC5H", "F5", "FFT7H", "FT7", "FTT7H"]),
    DefinedElectrode("FC3", "G", ["C3", "FCC3H", "FC1", "FFC3H", "F3", "FFC5H", "FC5", "FCC5H"]),
    DefinedElectrode("FC1", "P", ["C1", "FCC1H", "FCZ", "FFC1H", "F1", "FFC3H", "FC3", "FCC3H"]),
    DefinedElectrode("FCZ", "G", ["CZ", "FCC2H", "FC2", "FFC2H", "FZ", "FFC1H", "FC1", "FCC1H"]),
    DefinedElectrode("FC2", "P", ["C2", "FCC4H", "FC4", "FFC4H", "F4", "F2", "FFC2H", "FCZ", "FCC2H"]),
    DefinedElectrode("FC4", "G", ["C4", "FCC6H", "FC6", "FFC6H", "F4", "FFC4H", "FC2", "FCC4H"]),
    DefinedElectrode("FC6", "P", ["FTT8H", "FT8", "FFT8H", "F6", "FFC6H", "FC4", "FCC6H"]),
    DefinedElectrode("FT8", "G", ["FTT10H", "F8", "FFT8H", "FC6", "FTT8H"]),
    DefinedElectrode("FT10", "X", ["M1", "FTT10H"]),
    DefinedElectrode("FTT9H", "Y", ["T7", "FTT7H", "FT7", "FT9"]),
    DefinedElectrode("FTT7H", "Y", ["C5", "FCC5H", "FC5", "FT7", "FTT9H", "T7"]),
    DefinedElectrode("FCC5H", "X", ["CCP5H", "C3", "FCC3H", "FC3", "FFC5H", "FC5", "FTT7H", "C5"]),
    DefinedElectrode("FCC3H", "X", ["CCP3H", "C1", "FCC1H", "FC1", "FFC3H", "FC3", "FCC5H", "C3"]),
    DefinedElectrode("FCC1H", "Y", ["CCP1H", "CZ", "FCC2H", "FCZ", "FFC1H", "FC1", "FCC3H", "C1"]),
    DefinedElectrode("FCC2H", "Y", ["CCP2H", "C2", "FCC4H", "FC2", "FFC2H", "FCZ", "FCC1H", "CZ"]),
    DefinedElectrode("FCC4H", "X", ["CCP4H", "C4", "FCC6H", "FC4", "FFC4H", "FC2", "FCC2H", "C2"]),
    DefinedElectrode("FCC6H", "X", ["CCP6H", "C6", "FTT8H", "FC6", "FFC6H", "FC4", "FCC4H", "C4"]),
    DefinedElectrode("FTT8H", "Y", ["T8", "FT8", "FFT8H", "FC6", "FCC6H", "C6"]),
    DefinedElectrode("FTT10H", "Y", ["FT10", "FT8", "T8"]),
    DefinedElectrode("T7", "P", ["TP7", "TTP7H", "FTT7H", "FT7", "FTT9H"]),
    DefinedElectrode("C5", "G", ["CP5", "CCP5H", "C3", "FCC5H", "FC5", "FTT7H", "TTP7H"]),
    DefinedElectrode("C3", "P", ["CP3", "CCP3H", "C1", "FCC3H", "FC3", "FCC5H", "C5", "CCP5H"]),
    DefinedElectrode("C1", "G", ["CP1", "CCP1H", "CZ", "FCC1H", "FC1", "FCC3H", "C3", "CCP3H"]),
    DefinedElectrode("CZ", "P", ["CPZ", "CCP2H", "C2", "FCC2H", "FCZ", "FCC1H", "C1", "CCP1H"]),
    DefinedElectrode("C2", "G", ["CP2", "CCP4H", "C4", "FCC4H", "FC2", "FCC2H", "CZ", "CCP2H"]),
    DefinedElectrode("C4", "P", ["CP4", "CCP6H", "C6", "FCC6H", "FC4", "FCC4H", "C2", "CCP4H"]),
    DefinedElectrode("C6", "G", ["CP6", "TTP8H", "FTT8H", "FCC6H", "C4", "CCP6H"]),
    DefinedElectrode("T8", "P", ["FTT10H", "FTT8H", "TTP8H", "TP8"]),
    DefinedElectrode("M1", "P", ["FT10"]),
    DefinedElectrode("TTP7H", "Y", ["TPP7H", "CP5", "CCP5H", "C5", "T7", "TP7"]),
    DefinedElectrode("CCP5H", "X", ["CPP5H", "CP3", "CCP3H", "C3", "FCC5H", "C5", "TTP7H", "CP5"]),
    DefinedElectrode("CCP3H", "X", ["CPP3H", "CP1", "CCP1H", "C1", "FCC3H", "C3", "CCP5H", "CP3"]),
    DefinedElectrode("CCP1H", "Y", ["CPP1H", "CPZ", "CCP2H", "CZ", "FCC1H", "C1", "CCP3H", "CP1"]),
    DefinedElectrode("CCP2H", "Y", ["CPP2H", "CP2", "CCP4H", "C2", "FCC2H", "CZ", "CCP1H", "CPZ"]),
    DefinedElectrode("CCP4H", "X", ["CPP4H", "CP4", "CCP6H", "C4", "FCC4H", "C2", "CCP2H", "CP2"]),
    DefinedElectrode("CCP6H", "X", ["CP6", "C6", "FCC6H", "C4", "CCP4H", "CP4", "CPP6H"]),
    DefinedElectrode("TTP8H", "Y", ["TP8", "T8", "C6", "CP6", "TPP8H"]),
    DefinedElectrode("M2", "P", ["TPP10H"]),
    DefinedElectrode("TP7", "G", ["P7", "TPP7H", "CP5", "TTP7H", "T7", "TPP9H"]),
    DefinedElectrode("CP5", "P", ["P5", "CPP5H", "CP3", "CCP5H", "C5", "TTP7H", "TP7", "TPP7H"]),
    DefinedElectrode("CP3", "G", ["P3", "CPP3H", "CP1", "CCP3H", "C3", "CCP5H", "CP5", "CPP5H"]),
    DefinedElectrode("CP1", "P", ["P1", "CPP1H", "CPZ", "CCP1H", "C1", "CCP3H", "CP3", "CPP3H"]),
    DefinedElectrode("CPZ", "G", ["PZ", "CPP2H", "CP2", "CCP2H", "CZ", "CCP1H", "CP1", "CPP1H"]),
    DefinedElectrode("CP2", "P", ["CPP4H", "CP4", "CCP4H", "C2", "CCP2H", "CPZ", "CPP2H", "P2"]),
    DefinedElectrode("CP4", "G", ["CPP6H", "CP6", "CCP6H", "C4", "CCP4H", "CP2", "CPP4H", "P4"]),
    DefinedElectrode("CP6", "P", ["TPP8H", "TP8", "TTP8H", "C6", "CCP6H", "CP4", "CPP6H"]),
    DefinedElectrode("TP8", "G", ["T8", "TTP8H", "CP6", "TPP8H"]),
    DefinedElectrode("TPP9H", "X", ["PPO9H", "P7", "TPP7H", "TP7", "P9"]),
    DefinedElectrode("TPP7H", "Y", ["P7", "P5", "CP5", "TTP7H", "TP7", "TPP9H"]),
    DefinedElectrode("CPP5H", "X", ["PPO5H", "PO3", "P3", "CPP3H", "CP3", "CCP5H", "CP5", "P5"]),
    DefinedElectrode("CPP3H", "X", ["P1", "PPO1", "CPP1H", "CP1", "CCP3H", "CP3", "CPP5H", "P3"]),
    DefinedElectrode("CPP1H", "Y", ["PZ", "CPP2H", "CPZ", "CCP1H", "CP1", "CPP3H", "P1", "PPO1"]),
    DefinedElectrode("CPP2H", "Y", ["PPO2", "P2", "CPP4H", "CP2", "CCP2H", "CPZ", "CPP1H", "PZ"]),
    DefinedElectrode("CPP4H", "X", ["P4", "CPP6H", "CP4", "CCP4H", "CP2", "CPP2H", "P2"]),
    DefinedElectrode("CPP6H", "X", ["P6", "TPP8H", "CP6", "CCP6H", "CP4", "CPP4H", "P4", "PPO6H"]),
    DefinedElectrode("TPP8H", "Y", ["P8", "TP8", "TTP8H", "CP6", "CPP6H", "P6"]),
    DefinedElectrode("TPP10H", "X", ["P10", "M2", "P8"]),
    DefinedElectrode("P9", "X", ["PPO9H", "TPP9H"]),
    DefinedElectrode("P7", "P", ["PO7", "P5", "TPP7H", "TP7", "TPP9H", "PPO9H"]),
    DefinedElectrode("P5", "G", ["PO3", "PPO5H", "P3", "CPP5H", "CP5", "TPP7H", "P7"]),
    DefinedElectrode("P3", "P", ["PO3", "PPO1", "P1", "CPP3H", "CP3", "CPP5H", "P5", "PPO5H"]),
    DefinedElectrode("P1", "G", ["PPO1", "PZ", "CPP1H", "CP1", "CPP3H", "P3", "PO3"]),
    DefinedElectrode("PZ", "P", ["POZ", "PPO2", "P2", "CPP2H", "CPZ", "CPP1H", "P1", "PPO1"]),
    DefinedElectrode("P2", "G", ["PO4", "P4", "CPP4H", "CP2", "CPP2H", "PZ", "PPO2"]),
    DefinedElectrode("P4", "P", ["PPO6H", "P6", "CPP6H", "CP4", "CPP4H", "P2", "PPO2", "PO4"]),
    DefinedElectrode("P6", "G", ["P8", "TPP8H", "CPP6H", "P4", "PO4", "PPO6H", "PO8"]),
    DefinedElectrode("P8", "P", ["TPP10H", "TPP8H", "P6", "PO8", "PPO10H"]),
    DefinedElectrode("P10", "X", ["TPP10H", "PPO10H"]),
    DefinedElectrode("PPO9H", "Y", ["PO9", "PO7", "P7", "TPP9H", "P9"]),
    DefinedElectrode("PPO5H", "Y", ["PO3", "P3", "CPP5H", "P5"]),
    DefinedElectrode("PPO1", "X", ["POZ", "PPO2", "PZ", "CPP1H", "CPP3H", "P1", "P3", "PO3"]),
    DefinedElectrode("PPO2", "X", ["PO4", "P4", "P2", "CPP2H", "PZ", "PPO1", "POZ"]),
    DefinedElectrode("PPO6H", "Y", ["PO8", "P6", "CPP6H", "P4", "PO4"]),
    DefinedElectrode("PPO10H", "Y", ["P10", "P8", "PO8", "PO10"]),
    DefinedElectrode("PO9", "X", ["I1", "POO9H", "PO7", "PPO9H"]),
    DefinedElectrode("PO7", "G", ["POO9H", "O1", "P7", "PPO9H", "PO9"]),
    DefinedElectrode("PO3", "G", ["POO3H", "PPO1", "P1", "P3", "CPP5H", "PPO5H", "P5"]),
    DefinedElectrode("POZ", "P", ["POO4H", "PPO2", "PZ", "PPO1", "POO3H"]),
    DefinedElectrode("PO4", "G", ["PO8", "PPO6H", "P6", "P4", "P2", "PPO2", "POO4H"]),
    DefinedElectrode("PO8", "G", ["PO10", "PPO10H", "P8", "P6", "PPO6H", "PO4", "O2", "POO10H"]),
    DefinedElectrode("PO10", "X", ["PPO10H", "PO8", "POO10H", "I2"]),
    DefinedElectrode("POO9H", "Y", ["I1", "OI1H", "O1", "PO7", "PO9"]),
    DefinedElectrode("POO3H", "Y", ["POO4H", "POZ", "PO3", "O1", "OI1H"]),
    DefinedElectrode("POO4H", "Y", ["OI2H", "O2", "PO4", "POZ", "POO3H"]),
    DefinedElectrode("POO10H", "Y", ["I2", "PO10", "PO8", "O2", "OI2H"]),
    DefinedElectrode("O1", "P", ["OI1H", "POO3H", "PO7", "POO9H"]),
    DefinedElectrode("O2", "P", ["POO10H", "PO8", "POO4H", "OI2H"]),
    DefinedElectrode("OI1H", "Y", ["IZ", "OI2H", "POO3H", "O1", "POO9H", "I1"]),
    DefinedElectrode("OI2H", "Y", ["I2", "POO10H", "O2", "POO4H", "OI1H", "IZ"]),
    DefinedElectrode("I1", "X", ["IZ", "OI1H", "POO9H", "PO9"]),
    DefinedElectrode("IZ", "X", ["OI2H", "OI1H", "I1"]),
    DefinedElectrode("I2", "X", ["PO10", "POO10H", "OI2H"]),
]

definedElectrodes = [
    DefinedElectrode("FP1", "P", ["AFZ", "AFP3H", "FPZ", "AF3"]),
DefinedElectrode("FPZ", "P", ["AFZ", "AFP4H", "FP2", "FP1", "AFP3H"]),
DefinedElectrode("FP2", "P", ["AF4", "AF8", "FPZ", "AFP4H"]),
DefinedElectrode("AFP3H", "Y", ["AFF1", "AFZ", "AFP4H", "FPZ", "FP1", "AF3"]),
DefinedElectrode("AFP4H", "Y", ["AFF2", "AF4", "FP2", "FPZ", "AFP3H", "AFZ"]),
DefinedElectrode("AF7", "G", ["F5", "AFF5H", "AF3", "F7", "FFT7H"]),
DefinedElectrode("AF3", "G", ["FFC3H", "F1", "AFF1", "AFZ", "AFP3H", "FP1", "AF7", "F5", "AFF5H", "F3"]),
DefinedElectrode("AFZ", "X", ["FZ", "AFF2", "F2", "AF4", "AFP4H", "FPZ", "AFP3H", "FP1", "AF3", "AFF1", "F1"]),
DefinedElectrode("AF4", "G", ["FFC4H", "F4", "FFC6H", "F6", "AFF6H", "AF8", "FP2", "AFP4H", "AFZ", "AFF2", "F2"]),
DefinedElectrode("AF8", "G", ["F6", "F8", "FP2", "AF4", "AFF6H"]),
DefinedElectrode("AFF5H", "Y", ["FFC3H", "F3", "F1", "AFF1", "AF3", "AF7", "F7", "FFT7H", "F5", "FFC5H"]),
DefinedElectrode("AFF1", "X", ["FFC1H", "FFC2H", "FZ", "AFF2", "AFZ", "AFP3H", "AF3", "AFF5H", "F3", "FFC3H", "F1"]),
DefinedElectrode("AFF2", "X", ["FFC2H", "FFC4H", "F2", "F4", "AF4", "AFP4H", "AFZ", "AFF1", "F1", "FZ", "FFC1H"]),
DefinedElectrode("AFF6H", "Y", ["FFC6H", "FC6", "F6", "FFT8H", "F8", "AF8", "AF4", "F2", "F4", "FFC4H", "FC4"]),
DefinedElectrode("F7", "P", ["FC5", "FFT7H", "FFC5H", "F5", "AFF5H", "AF7", "FT7"]),
DefinedElectrode("F5", "G", ["FFC5H", "FC3", "FFC3H", "F3", "AFF5H", "AF3", "AF7", "F7", "FFT7H", "FC5"]),
DefinedElectrode("F3", "P", ["FFC3H", "FC1", "FFC1H", "F1", "AFF1", "AF3", "AFF5H", "F5", "FFT7H", "FFC5H", "FC3"]),
DefinedElectrode("F1", "G", ["FC1", "FFC1H", "FCZ", "FFC2H", "FZ", "AFF2", "AFZ", "AFF1", "AF3", "AFF5H", "F3", "FFC5H", "FC3", "FFC3H"]),
DefinedElectrode("FZ", "P", ["FCZ", "FC2", "FFC2H", "F2", "AFF2", "AFZ", "AFF1", "F1", "FC1", "FFC1H"]),
DefinedElectrode("F2", "G", ["FC2", "FFC4H", "FC4", "FFC6H", "F4", "AFF6H", "AF4", "AFZ", "AFF2", "FZ", "FFC1H", "FFC2H", "FCZ"]),
DefinedElectrode("F4", "P", ["FC4", "FFC6H", "F6", "AFF6H", "AF4", "AFF2", "F2", "FFC2H", "FC2", "FFC4H"]),
DefinedElectrode("F6", "G", ["FC6", "FFT8H", "F8", "AF8", "AFF6H", "AF4", "F4", "FFC4H", "FFC6H", "FC4"]),
DefinedElectrode("F8", "P", ["FFT8H", "FT8", "AF8", "AFF6H", "F6", "FFC6H", "FC6"]),
DefinedElectrode("FFT7H", "Y", ["FC5", "FFC5H", "F3", "F5", "AFF5H", "AF7", "F7", "FT7", "FTT7H"]),
DefinedElectrode("FFC5H", "X", ["FC3", "FCC3H", "FC1", "FFC3H", "F1", "F3", "AFF5H", "F5", "F7", "FFT7H", "FC5", "FCC5H"]),
DefinedElectrode("FFC3H", "X", ["FCC3H", "FCC1H", "FC1", "FCZ", "FFC1H", "F1", "AFF1", "AF3", "F3", "AFF5H", "F5", "FFC5H", "FCC5H", "FC3"]),
DefinedElectrode("FFC1H", "Y", ["FCC1H", "FCC2H", "FCZ", "FC2", "FFC2H", "F2", "AFF2", "FZ", "AFF1", "F1", "F3", "FFC3H", "FC1"]),
DefinedElectrode("FFC2H", "Y", ["FCC2H", "FC2", "FFC4H", "F4", "F2", "AFF2", "FZ", "AFF1", "F1", "FFC1H", "FCZ"]),
DefinedElectrode("FFC4H", "X", ["FCC4H", "FC4", "FCC6H", "FFC6H", "F6", "AFF6H", "F4", "AF4", "F2", "AFF2", "FFC2H", "FCZ", "FC2", "FCC2H", "C2"]),
DefinedElectrode("FFC6H", "X", ["FCC6H", "FC6", "FFT8H", "F8", "F6", "AFF6H", "AF4", "F4", "F2", "FFC4H", "FC2", "FC4", "FCC4H"]),
DefinedElectrode("FFT8H", "Y", ["FTT8H", "FT8", "F8", "AFF6H", "F6", "FFC6H", "FC6"]),
DefinedElectrode("FT9", "X", ["FTT9H", "FT7"]),
DefinedElectrode("FT7", "G", ["FTT7H", "FC5", "FFT7H", "F7", "FT9", "FTT9H", "T7"]),
DefinedElectrode("FC5", "P", ["C5", "FCC5H", "C3", "FC3", "FFC5H", "F5", "FFT7H", "F7", "FT7", "FTT7H"]),
DefinedElectrode("FC3", "G", ["C3", "FCC3H", "C1", "FCC1H", "FC1", "FFC3H", "F1", "F3", "F5", "FFC5H", "FC5", "FCC5H"]),
DefinedElectrode("FC1", "P", ["C1", "FCC1H", "CZ", "FCZ", "FFC1H", "FZ", "F1", "F3", "FFC3H", "FFC5H", "FC3", "FCC3H"]),
DefinedElectrode("FCZ", "G", ["CZ", "FCC2H", "FC2", "FFC4H", "F2", "FFC2H", "FZ", "F1", "FFC1H", "FFC3H", "FC1", "FCC1H"]),
DefinedElectrode("FC2", "P", ["C2", "FCC4H", "FC4", "FFC6H", "FFC4H", "F4", "F2", "FFC2H", "FZ", "FFC1H", "FCZ", "CZ", "FCC2H"]),
DefinedElectrode("FC4", "G", ["C4", "FCC6H", "FC6", "F6", "FFC6H", "AFF6H", "F4", "F2", "FFC4H", "FC2", "FCC2H", "C2", "FCC4H"]),
DefinedElectrode("FC6", "P", ["C6", "FTT8H", "FT8", "FFT8H", "F8", "F6", "AFF6H", "FFC6H", "FC4", "FCC6H"]),
DefinedElectrode("FT8", "G", ["T8", "FTT10H", "FT10", "F8", "FFT8H", "FC6", "FTT8H"]),
DefinedElectrode("FT10", "X", ["M1", "FT8", "FTT10H"]),
DefinedElectrode("FTT9H", "Y", ["T7", "FTT7H", "FT7", "FT9"]),
DefinedElectrode("FTT7H", "Y", ["TTP7H", "C5", "CCP5H", "FCC5H", "FC5", "FFT7H", "FT7", "FTT9H", "T7"]),
DefinedElectrode("FCC5H", "X", ["CCP5H", "CCP3H", "C3", "FCC3H", "FC3", "FFC3H", "FFC5H", "FC5", "FTT7H", "C5"]),
DefinedElectrode("FCC3H", "X", ["CCP3H", "CCP1H", "C1", "FCC1H", "FC1", "FFC3H", "FFC5H", "FC3", "FCC5H", "C3", "CCP5H"]),
DefinedElectrode("FCC1H", "Y", ["CCP1H", "CCP2H", "CZ", "FCC2H", "FCZ", "FFC1H", "FC1", "FFC3H", "FC3", "FCC3H", "C1", "CCP3H"]),
DefinedElectrode("FCC2H", "Y", ["CCP2H", "C2", "FCC4H", "FC4", "FFC4H", "FC2", "FFC2H", "FCZ", "FFC1H", "FCC1H", "CZ"]),
DefinedElectrode("FCC4H", "X", ["CCP4H", "C4", "FCC6H", "FFC6H", "FC4", "FFC4H", "FC2", "FCC2H", "C2", "CCP2H"]),
DefinedElectrode("FCC6H", "X", ["CCP6H", "C6", "FTT8H", "FC6", "FFC6H", "FFC4H", "FC4", "FCC4H", "C4", "CCP4H"]),
DefinedElectrode("FTT8H", "Y", ["TTP8H", "T8", "FTT10H", "FT8", "FFT8H", "FC6", "FCC6H", "C6"]),
DefinedElectrode("FTT10H", "Y", ["FT10", "FT8", "FTT8H", "T8"]),
DefinedElectrode("T7", "P", ["TP7", "TTP7H", "C5", "FTT7H", "FT7", "FTT9H"]),
DefinedElectrode("C5", "G", ["CP5", "CP3", "CCP5H", "C3", "FCC5H", "FC5", "FTT7H", "T7", "TTP7H"]),
DefinedElectrode("C3", "P", ["CP3", "CP1", "CCP3H", "C1", "FCC3H", "FC3", "FC5", "FCC5H", "C5", "CCP5H"]),
DefinedElectrode("C1", "G", ["CP1", "CCP1H", "CPZ", "CCP2H", "CZ", "FCC1H", "FC1", "FC3", "FCC3H", "C3", "CP3", "CCP3H"]),
DefinedElectrode("CZ", "P", ["CPZ", "CCP2H", "CP2", "C2", "FCC2H", "FC2", "FCZ", "FC1", "FCC1H", "C1", "CCP1H"]),
DefinedElectrode("C2", "G", ["CP2", "CCP4H", "CP4", "C4", "FCC4H", "FC4", "FFC4H", "FC2", "FCC2H", "CZ", "CCP2H"]),
DefinedElectrode("C4", "P", ["CP4", "CCP6H", "C6", "FCC6H", "FC4", "FCC4H", "C2", "CCP4H", "CP2"]),
DefinedElectrode("C6", "G", ["CP6", "TTP8H", "T8", "FTT8H", "FC6", "FCC6H", "C4", "CCP6H"]),
DefinedElectrode("T8", "P", ["FTT10H", "FT8", "FTT8H", "C6", "TTP8H", "TP8"]),
DefinedElectrode("M1", "P", ["FT10"]),
DefinedElectrode("TTP7H", "Y", ["TPP7H", "P5", "CPP5H", "CP5", "CCP5H", "C5", "FTT7H", "T7", "TP7"]),
DefinedElectrode("CCP5H", "X", ["CPP5H", "CP3", "CPP3H", "CCP3H", "FCC3H", "C3", "FCC5H", "FTT7H", "C5", "TTP7H", "CP5"]),
DefinedElectrode("CCP3H", "X", ["CPP3H", "CPP1H", "CP1", "CPZ", "CCP1H", "FCC1H", "C1", "FCC3H", "C3", "FCC5H", "CCP5H", "CP3"]),
DefinedElectrode("CCP1H", "Y", ["CPP1H", "CPP2H", "CPZ", "CCP2H", "CZ", "FCC1H", "C1", "FCC3H", "CCP3H", "CP1", "CPP3H"]),
DefinedElectrode("CCP2H", "Y", ["CPP2H", "CPP4H", "CP2", "CP4", "CCP4H", "FCC4H", "C2", "FCC2H", "CZ", "FCC1H", "C1", "CCP1H", "CPZ", "CPP1H"]),
DefinedElectrode("CCP4H", "X", ["CPP4H", "CP4", "CCP6H", "FCC6H", "C4", "FCC4H", "C2", "CCP2H", "CP2", "CPP2H"]),
DefinedElectrode("CCP6H", "X", ["CP6", "TTP8H", "C6", "FCC6H", "C4", "CCP4H", "CP4", "CPP4H", "CPP6H"]),
DefinedElectrode("TTP8H", "Y", ["TP8", "T8", "FTT8H", "C6", "CCP6H", "CP6", "TPP8H"]),
DefinedElectrode("M2", "P", ["TP8", "TPP10H"]),
DefinedElectrode("TP7", "G", ["P7", "TPP7H", "P5", "CP5", "TTP7H", "T7", "TPP9H"]),
DefinedElectrode("CP5", "P", ["P5", "PPO5H", "P3", "CPP5H", "CP3", "CCP5H", "C5", "TTP7H", "TP7", "TPP7H", "P7"]),
DefinedElectrode("CP3", "G", ["P3", "P1", "CPP3H", "CPP1H", "CP1", "CCP3H", "C1", "C3", "CCP5H", "C5", "CP5", "CPP5H", "P5", "PPO5H"]),
DefinedElectrode("CP1", "P", ["P1", "PPO1", "PZ", "CPP1H", "CPP2H", "CPZ", "CCP1H", "C1", "CCP3H", "C3", "CP3", "CPP3H", "P3"]),
DefinedElectrode("CPZ", "G", ["PZ", "P2", "CPP2H", "CPP4H", "CP2", "CCP2H", "CZ", "C1", "CCP1H", "CCP3H", "CP1", "CPP3H", "P1", "CPP1H"]),
DefinedElectrode("CP2", "P", ["P4", "CPP4H", "CP4", "C4", "CCP4H", "C2", "CZ", "CCP2H", "CPZ", "PZ", "CPP2H", "P2"]),
DefinedElectrode("CP4", "G", ["CPP6H", "CP6", "CCP6H", "C4", "C2", "CCP4H", "CCP2H", "CP2", "CPP2H", "P2", "CPP4H", "P4"]),
DefinedElectrode("CP6", "P", ["TPP8H", "TP8", "TTP8H", "C6", "CCP6H", "CP4", "P4", "CPP6H", "P6"]),
DefinedElectrode("TP8", "G", ["TPP10H", "M2", "T8", "TTP8H", "CP6", "TPP8H", "P8"]),
DefinedElectrode("TPP9H", "X", ["PPO9H", "P7", "P5", "TPP7H", "TP7", "P9"]),
DefinedElectrode("TPP7H", "Y", ["P7", "PPO5H", "P5", "CPP5H", "CP5", "TTP7H", "TP7", "TPP9H", "PPO9H"]),
DefinedElectrode("CPP5H", "X", ["PPO5H", "PO3", "P3", "P1", "CPP3H", "CP3", "CCP5H", "CP5", "TTP7H", "TPP7H", "P7", "P5"]),
DefinedElectrode("CPP3H", "X", ["P1", "PPO1", "PZ", "CPP1H", "CPZ", "CCP1H", "CP1", "CCP3H", "CCP5H", "CP3", "CPP5H", "P3", "PPO5H", "PO3"]),
DefinedElectrode("CPP1H", "Y", ["PZ", "PPO2", "P2", "CPP2H", "CCP2H", "CPZ", "CCP1H", "CP1", "CCP3H", "CP3", "CPP3H", "P3", "P1", "PPO1"]),
DefinedElectrode("CPP2H", "Y", ["PPO2", "P2", "P4", "CPP4H", "CP4", "CCP4H", "CP2", "CCP2H", "CPZ", "CCP1H", "CP1", "CPP1H", "P1", "PZ", "PPO1"]),
DefinedElectrode("CPP4H", "X", ["PO4", "P4", "PPO6H", "P6", "CPP6H", "CCP6H", "CP4", "CCP4H", "CP2", "CCP2H", "CPZ", "CPP2H", "PZ", "P2", "PPO2"]),
DefinedElectrode("CPP6H", "X", ["P6", "P8", "TPP8H", "CP6", "CCP6H", "CP4", "CPP4H", "P2", "P4", "PO4", "PPO6H"]),
DefinedElectrode("TPP8H", "Y", ["PPO10H", "P8", "TPP10H", "TP8", "TTP8H", "CP6", "CPP6H", "P6", "PPO6H"]),
DefinedElectrode("TPP10H", "X", ["P10", "M2", "TP8", "TPP8H", "P8", "PPO10H"]),
DefinedElectrode("P9", "X", ["PPO9H", "TPP9H"]),
DefinedElectrode("P7", "P", ["PO7", "PPO5H", "P5", "CPP5H", "CP5", "TPP7H", "TP7", "TPP9H", "PPO9H"]),
DefinedElectrode("P5", "G", ["PO7", "PO3", "PPO5H", "P3", "CP3", "CPP5H", "CP5", "TTP7H", "TP7", "TPP7H", "TPP9H", "P7"]),
DefinedElectrode("P3", "P", ["PO3", "PPO1", "P1", "CPP1H", "CP1", "CPP3H", "CP3", "CPP5H", "CP5", "P5", "PPO5H"]),
DefinedElectrode("P1", "G", ["POZ", "PPO1", "PPO2", "PZ", "CPP2H", "CPP1H", "CPZ", "CP1", "CPP3H", "CP3", "CPP5H", "P3", "PPO5H", "PO3"]),
DefinedElectrode("PZ", "P", ["POZ", "PPO2", "P2", "CPP4H", "CPP2H", "CP2", "CPZ", "CPP1H", "CP1", "CPP3H", "P1", "PPO1"]),
DefinedElectrode("P2", "G", ["PO4", "PPO6H", "P4", "CPP6H", "CPP4H", "CP4", "CP2", "CPP2H", "CPZ", "CPP1H", "PZ", "PPO1", "POZ", "PPO2"]),
DefinedElectrode("P4", "P", ["PPO6H", "P6", "CPP6H", "CP6", "CP4", "CPP4H", "CP2", "CPP2H", "P2", "PPO2", "PO4"]),
DefinedElectrode("P6", "G", ["PPO10H", "P8", "TPP8H", "CP6", "CPP6H", "CPP4H", "P4", "PO4", "PPO6H", "PO8"]),
DefinedElectrode("P8", "P", ["P10", "TPP10H", "TP8", "TPP8H", "CPP6H", "P6", "PPO6H", "PO8", "PO10", "PPO10H"]),
DefinedElectrode("P10", "X", ["TPP10H", "P8", "PPO10H", "PO10"]),
DefinedElectrode("PPO9H", "Y", ["PO9", "PO7", "P7", "TPP7H", "TPP9H", "P9"]),
DefinedElectrode("PPO5H", "Y", ["PO3", "PPO1", "P1", "CPP3H", "P3", "CP3", "CPP5H", "CP5", "P5", "TPP7H", "P7", "PO7"]),
DefinedElectrode("PPO1", "X", ["POZ", "PPO2", "P2", "CPP2H", "PZ", "CPP1H", "CP1", "CPP3H", "P1", "P3", "PPO5H", "PO3", "POO3H"]),
DefinedElectrode("PPO2", "X", ["POO4H", "PO4", "PPO6H", "P4", "CPP4H", "P2", "CPP2H", "CPP1H", "PZ", "P1", "PPO1", "POZ"]),
DefinedElectrode("PPO6H", "Y", ["PO8", "PPO10H", "P8", "TPP8H", "P6", "CPP6H", "CPP4H", "P4", "P2", "PPO2", "PO4"]),
DefinedElectrode("PPO10H", "Y", ["P10", "TPP10H", "P8", "TPP8H", "P6", "PPO6H", "PO8", "POO10H", "PO10"]),
DefinedElectrode("PO9", "X", ["I1", "POO9H", "O1", "PO7", "PPO9H"]),
DefinedElectrode("PO7", "G", ["POO9H", "O1", "POO3H", "PO3", "PPO5H", "P5", "P7", "PPO9H", "PO9"]),
DefinedElectrode("PO3", "G", ["O1", "POO3H", "POZ", "PPO1", "P1", "CPP3H", "P3", "CPP5H", "PPO5H", "P5", "PO7"]),
DefinedElectrode("POZ", "P", ["O2", "POO4H", "PO4", "PPO2", "P2", "PZ", "PPO1", "P1", "PO3", "POO3H"]),
DefinedElectrode("PO4", "G", ["PO8", "PPO6H", "P6", "CPP6H", "P4", "CPP4H", "P2", "PPO2", "POZ", "POO4H", "O2"]),
DefinedElectrode("PO8", "G", ["PO10", "PPO10H", "P8", "P6", "PPO6H", "PO4", "POO4H", "O2", "POO10H"]),
DefinedElectrode("PO10", "X", ["P10", "PPO10H", "P8", "PO8", "O2", "POO10H", "I2"]),
DefinedElectrode("POO9H", "Y", ["I1", "OI1H", "POO3H", "O1", "PO7", "PO9"]),
DefinedElectrode("POO3H", "Y", ["POO4H", "POZ", "PPO1", "PO3", "PO7", "O1", "POO9H", "OI1H"]),
DefinedElectrode("POO4H", "Y", ["OI2H", "O2", "POO10H", "PO8", "PO4", "PPO2", "POZ", "POO3H"]),
DefinedElectrode("POO10H", "Y", ["I2", "PO10", "PPO10H", "PO8", "POO4H", "O2", "OI2H"]),
DefinedElectrode("O1", "P", ["OI1H", "POO3H", "PO3", "PO7", "PO9", "POO9H", "I1"]),
DefinedElectrode("O2", "P", ["I2", "POO10H", "PO10", "PO8", "PO4", "POO4H", "POZ", "OI2H"]),
DefinedElectrode("OI1H", "Y", ["IZ", "OI2H", "POO3H", "O1", "POO9H", "I1"]),
DefinedElectrode("OI2H", "Y", ["I2", "POO10H", "O2", "POO4H", "OI1H", "IZ"]),
DefinedElectrode("I1", "X", ["IZ", "OI1H", "O1", "POO9H", "PO9"]),
DefinedElectrode("IZ", "X", ["I2", "OI2H", "OI1H", "I1"]),
DefinedElectrode("I2", "X", ["PO10", "POO10H", "O2", "OI2H", "IZ"]),

]
"""

definedElectrodes = [
    DefinedElectrode("FP1", "P", 25.447912998908187, ["FPZ", "AFP3H"]),
DefinedElectrode("FPZ", "P", 0.0, ["AFP3H", "FP1", "AFP4H"]),
DefinedElectrode("FP2", "P", 34.64546123231728, ["AFP4H", "AF8", "AF4"]),
DefinedElectrode("AFP3H", "Y", 13.055658849709582, ["FP1", "FPZ", "AFP4H", "AFZ"]),
DefinedElectrode("AFP4H", "Y", 18.370110642018464, ["AFZ", "AFP3H", "FPZ", "FP2", "AF4"]),
DefinedElectrode("AF7", "G", 65.81131489341327, ["F7", "AFF5H", "F5"]),
DefinedElectrode("AF3", "G", 40.51672781703873, ["F3", "AFF5H", "AFF1", "F1"]),
DefinedElectrode("AFZ", "X", 10.715694517855582, ["AFF1", "AFP3H", "AFP4H", "AFF2", "FZ"]),
DefinedElectrode("AF4", "G", 44.57458945408247, ["F2", "AFF2", "AFP4H", "FP2", "AFF6H", "F4"]),
DefinedElectrode("AF8", "G", 64.00597460393836, ["AFF6H", "FP2", "F8"]),
DefinedElectrode("AFF5H", "Y", 60.947663819050526, ["FFC5H", "F5", "AF7", "AF3", "F3"]),
DefinedElectrode("AFF1", "X", 26.481548463033654, ["F1", "AF3", "AFZ", "AFF2", "FZ", "FFC1H"]),
DefinedElectrode("AFF2", "X", 27.95583139525634, ["FZ", "AFF1", "AFZ", "AF4", "F2", "FFC2H"]),
DefinedElectrode("AFF6H", "Y", 71.18914423562065, ["F4", "AF4", "AF8", "F8", "F6", "FFC6H"]),
DefinedElectrode("F7", "P", 84.64278426422419, ["AF7", "F5", "FFT7H"]),
DefinedElectrode("F5", "G", 75.62924667745938, ["FC5", "FFT7H", "F7", "AF7", "AFF5H", "F3", "FFC5H"]),
DefinedElectrode("F3", "P", 60.782278601579264, ["FC3", "FFC5H", "F5", "AFF5H", "AF3", "F1", "FFC3H"]),
DefinedElectrode("F1", "G", 41.01756659042563, ["FFC3H", "F3", "AF3", "AFF1", "FZ", "FFC1H", "FC1"]),
DefinedElectrode("FZ", "P", 29.92084632827087, ["FFC1H", "F1", "AFF1", "AFZ", "AFF2", "F2", "FFC2H", "FCZ"]),
DefinedElectrode("F2", "G", 45.82700619721957, ["FFC2H", "FZ", "AFF2", "AF4", "F4", "FFC4H", "FC2"]),
DefinedElectrode("F4", "P", 63.56717152744804, ["FFC4H", "FC2", "F2", "AF4", "AFF6H", "F6", "FFC6H", "FC4"]),
DefinedElectrode("F6", "G", 83.0292282271731, ["FFC6H", "F4", "AFF6H", "F8", "FFT8H", "FC6"]),
DefinedElectrode("F8", "P", 88.8120979371617, ["F6", "AFF6H", "AF8", "FT8", "FFT8H"]),
DefinedElectrode("FFT7H", "Y", 90.45628516029166, ["FT7", "F7", "F5", "FFC5H", "FC5"]),
DefinedElectrode("FFC5H", "X", 80.59598159958101, ["FCC5H", "FC5", "FFT7H", "F5", "AFF5H", "F3", "FFC3H", "FC3"]),
DefinedElectrode("FFC3H", "X", 64.64247003325292, ["FC3", "FFC5H", "F3", "F1", "FFC1H", "FC1", "FCC3H"]),
DefinedElectrode("FFC1H", "Y", 45.43635119593122, ["FC1", "FFC3H", "F1", "AFF1", "FZ", "FFC2H", "FCZ", "FCC1H"]),
DefinedElectrode("FFC2H", "Y", 45.866557402970635, ["FCZ", "FFC1H", "FZ", "AFF2", "F2", "FFC4H", "FC2", "FCC2H"]),
DefinedElectrode("FFC4H", "X", 68.77343711055892, ["FC2", "FFC2H", "F2", "F4", "FFC6H", "FC4", "FCC4H"]),
DefinedElectrode("FFC6H", "X", 82.63723156059864, ["FC4", "FFC4H", "F4", "AFF6H", "F6", "FC6", "FCC6H"]),
DefinedElectrode("FFT8H", "Y", 101.79505592119885, ["FC6", "F6", "F8", "FT8", "FTT8H"]),
DefinedElectrode("FT9", "X", 106.28148614881145, ["FTT9H"]),
DefinedElectrode("FT7", "G", 109.95648150973183, ["T7", "FTT9H", "FFT7H", "FC5", "FTT7H"]),
DefinedElectrode("FC5", "P", 103.22708158714941, ["FTT7H", "FT7", "FFT7H", "F5", "FFC5H", "FC3", "FCC5H", "C5"]),
DefinedElectrode("FC3", "G", 85.66534408382424, ["FCC5H", "FC5", "FFC5H", "F3", "FFC3H", "FC1", "FCC3H", "C3"]),
DefinedElectrode("FC1", "P", 67.3849836462101, ["FCC3H", "FC3", "FFC3H", "F1", "FFC1H", "FCZ", "FCC1H", "C1"]),
DefinedElectrode("FCZ", "G", 56.67272911198119, ["FCC1H", "FC1", "FFC1H", "FZ", "FFC2H", "FC2", "FCC2H", "CZ"]),
DefinedElectrode("FC2", "P", 70.18002325448461, ["FCC2H", "FCZ", "FFC2H", "F2", "F4", "FFC4H", "FC4", "FCC4H", "C2"]),
DefinedElectrode("FC4", "G", 87.69604362797675, ["FCC4H", "FC2", "FFC4H", "F4", "FFC6H", "FC6", "FCC6H", "C4"]),
DefinedElectrode("FC6", "P", 103.08953460463384, ["FCC6H", "FC4", "FFC6H", "F6", "FFT8H", "FT8", "FTT8H"]),
DefinedElectrode("FT8", "G", 106.4518249960986, ["FTT8H", "FC6", "FFT8H", "F8", "FTT10H"]),
DefinedElectrode("FT10", "X", 104.94261171230684, ["FTT10H", "M1"]),
DefinedElectrode("FTT9H", "Y", 118.63593186298999, ["FT9", "FT7", "FTT7H", "T7"]),
DefinedElectrode("FTT7H", "Y", 119.28461441443321, ["T7", "FTT9H", "FT7", "FC5", "FCC5H", "C5"]),
DefinedElectrode("FCC5H", "X", 108.61604416475497, ["C5", "FTT7H", "FC5", "FFC5H", "FC3", "FCC3H", "C3", "CCP5H"]),
DefinedElectrode("FCC3H", "X", 92.09616728724384, ["C3", "FCC5H", "FC3", "FFC3H", "FC1", "FCC1H", "C1", "CCP3H"]),
DefinedElectrode("FCC1H", "Y", 79.5496400808954, ["C1", "FCC3H", "FC1", "FFC1H", "FCZ", "FCC2H", "CZ", "CCP1H"]),
DefinedElectrode("FCC2H", "Y", 77.18142021238013, ["CZ", "FCC1H", "FCZ", "FFC2H", "FC2", "FCC4H", "C2", "CCP2H"]),
DefinedElectrode("FCC4H", "X", 95.81809729899672, ["C2", "FCC2H", "FC2", "FFC4H", "FC4", "FCC6H", "C4", "CCP4H"]),
DefinedElectrode("FCC6H", "X", 111.0333360977684, ["C4", "FCC4H", "FC4", "FFC6H", "FC6", "FTT8H", "C6", "CCP6H"]),
DefinedElectrode("FTT8H", "Y", 119.26278931837876, ["C6", "FCC6H", "FC6", "FFT8H", "FT8", "T8"]),
DefinedElectrode("FTT10H", "Y", 119.16547196650548, ["T8", "FT8", "FT10"]),
DefinedElectrode("T7", "P", 132.27013060400296, ["FTT9H", "FT7", "FTT7H", "TTP7H", "TP7"]),
DefinedElectrode("C5", "G", 129.4576837310169, ["TTP7H", "FTT7H", "FC5", "FCC5H", "C3", "CCP5H", "CP5"]),
DefinedElectrode("C3", "P", 113.64337231884666, ["CCP5H", "C5", "FCC5H", "FC3", "FCC3H", "C1", "CCP3H", "CP3"]),
DefinedElectrode("C1", "G", 100.11200083906026, ["CCP3H", "C3", "FCC3H", "FC1", "FCC1H", "CZ", "CCP1H", "CP1"]),
DefinedElectrode("CZ", "P", 92.35408653654693, ["CCP1H", "C1", "FCC1H", "FCZ", "FCC2H", "C2", "CCP2H", "CPZ"]),
DefinedElectrode("C2", "G", 101.38963432718357, ["CCP2H", "CZ", "FCC2H", "FC2", "FCC4H", "C4", "CCP4H", "CP2"]),
DefinedElectrode("C4", "P", 117.09130092368092, ["CCP4H", "C2", "FCC4H", "FC4", "FCC6H", "C6", "CCP6H", "CP4"]),
DefinedElectrode("C6", "G", 129.70056515682575, ["CCP6H", "C4", "FCC6H", "FTT8H", "TTP8H", "CP6"]),
DefinedElectrode("T8", "P", 132.52633902737978, ["TP8", "TTP8H", "FTT8H", "FTT10H"]),
DefinedElectrode("M1", "P", 142.67191897847312, ["FT10"]),
DefinedElectrode("TTP7H", "Y", 144.69097236870033, ["TP7", "T7", "C5", "CCP5H", "CP5", "TPP7H"]),
DefinedElectrode("CCP5H", "X", 134.57962280003613, ["CP5", "TTP7H", "C5", "FCC5H", "C3", "CCP3H", "CP3", "CPP5H"]),
DefinedElectrode("CCP3H", "X", 121.04876090650413, ["CP3", "CCP5H", "C3", "FCC3H", "C1", "CCP1H", "CP1", "CPP3H"]),
DefinedElectrode("CCP1H", "Y", 115.55480540851602, ["CP1", "CCP3H", "C1", "FCC1H", "CZ", "CCP2H", "CPZ", "CPP1H"]),
DefinedElectrode("CCP2H", "Y", 113.65541892052487, ["CPZ", "CCP1H", "CZ", "FCC2H", "C2", "CCP4H", "CP2", "CPP2H"]),
DefinedElectrode("CCP4H", "X", 124.47329442896579, ["CP2", "CCP2H", "C2", "FCC4H", "C4", "CCP6H", "CP4", "CPP4H"]),
DefinedElectrode("CCP6H", "X", 137.31110843628056, ["CPP6H", "CP4", "CCP4H", "C4", "FCC6H", "C6", "CP6"]),
DefinedElectrode("TTP8H", "Y", 142.48886561763345, ["TPP8H", "CP6", "C6", "T8", "TP8"]),
DefinedElectrode("M2", "P", 149.8223632472803, ["TPP10H"]),
DefinedElectrode("TP7", "G", 150.49573180990882, ["TPP9H", "T7", "TTP7H", "CP5", "TPP7H", "P7"]),
DefinedElectrode("CP5", "P", 151.783748866603, ["TPP7H", "TP7", "TTP7H", "C5", "CCP5H", "CP3", "CPP5H", "P5"]),
DefinedElectrode("CP3", "G", 142.1651092814267, ["CPP5H", "CP5", "CCP5H", "C3", "CCP3H", "CP1", "CPP3H", "P3"]),
DefinedElectrode("CP1", "P", 133.7187113645656, ["CPP3H", "CP3", "CCP3H", "C1", "CCP1H", "CPZ", "CPP1H", "P1"]),
DefinedElectrode("CPZ", "G", 130.72867947393948, ["CPP1H", "CP1", "CCP1H", "CZ", "CCP2H", "CP2", "CPP2H", "PZ"]),
DefinedElectrode("CP2", "P", 134.43224560350095, ["P2", "CPP2H", "CPZ", "CCP2H", "C2", "CCP4H", "CP4", "CPP4H"]),
DefinedElectrode("CP4", "G", 142.78341038790185, ["P4", "CPP4H", "CP2", "CCP4H", "C4", "CCP6H", "CP6", "CPP6H"]),
DefinedElectrode("CP6", "P", 149.93534414873633, ["CPP6H", "CP4", "CCP6H", "C6", "TTP8H", "TP8", "TPP8H"]),
DefinedElectrode("TP8", "G", 150.01118968930285, ["TPP8H", "CP6", "TTP8H", "T8"]),
DefinedElectrode("TPP9H", "X", 160.70659172852868, ["P9", "TP7", "TPP7H", "P7", "PPO9H"]),
DefinedElectrode("TPP7H", "Y", 161.82852736461516, ["TPP9H", "TP7", "TTP7H", "CP5", "P5", "P7"]),
DefinedElectrode("CPP5H", "X", 158.32757441456621, ["P5", "CP5", "CCP5H", "CP3", "CPP3H", "P3", "PO3", "PPO5H"]),
DefinedElectrode("CPP3H", "X", 148.2817059046732, ["P3", "CPP5H", "CP3", "CCP3H", "CP1", "CPP1H", "PPO1", "P1"]),
DefinedElectrode("CPP1H", "Y", 148.33498255637474, ["PPO1", "P1", "CPP3H", "CP1", "CCP1H", "CPZ", "CPP2H", "PZ"]),
DefinedElectrode("CPP2H", "Y", 149.2691861604397, ["PZ", "CPP1H", "CPZ", "CCP2H", "CP2", "CPP4H", "P2", "PPO2"]),
DefinedElectrode("CPP4H", "X", 151.78226714936105, ["P2", "CPP2H", "CP2", "CCP4H", "CP4", "CPP6H", "P4"]),
DefinedElectrode("CPP6H", "X", 159.89795999324068, ["PPO6H", "P4", "CPP4H", "CP4", "CCP6H", "CP6", "TPP8H", "P6"]),
DefinedElectrode("TPP8H", "Y", 159.5777676369738, ["P6", "CPP6H", "CP6", "TTP8H", "TP8", "P8"]),
DefinedElectrode("TPP10H", "X", 161.31037583491027, ["P8", "M2", "P10"]),
DefinedElectrode("P9", "X", 157.18946785646932, ["TPP9H", "PPO9H"]),
DefinedElectrode("P7", "P", 169.74751759598726, ["PPO9H", "TPP9H", "TP7", "TPP7H", "P5", "PO7"]),
DefinedElectrode("P5", "G", 170.1245717378886, ["P7", "TPP7H", "CP5", "CPP5H", "P3", "PPO5H", "PO3"]),
DefinedElectrode("P3", "P", 165.0197814960376, ["PPO5H", "P5", "CPP5H", "CP3", "CPP3H", "P1", "PPO1", "PO3"]),
DefinedElectrode("P1", "G", 161.83587370543034, ["PO3", "P3", "CPP3H", "CP1", "CPP1H", "PZ", "PPO1"]),
DefinedElectrode("PZ", "P", 160.04204223265836, ["PPO1", "P1", "CPP1H", "CPZ", "CPP2H", "P2", "PPO2", "POZ"]),
DefinedElectrode("P2", "G", 159.89118926632574, ["PPO2", "PZ", "CPP2H", "CP2", "CPP4H", "P4", "PO4"]),
DefinedElectrode("P4", "P", 166.4942954848604, ["PO4", "PPO2", "P2", "CPP4H", "CP4", "CPP6H", "P6", "PPO6H"]),
DefinedElectrode("P6", "G", 169.18545929541347, ["PO8", "PPO6H", "PO4", "P4", "CPP6H", "TPP8H", "P8"]),
DefinedElectrode("P8", "P", 168.3904141600703, ["PPO10H", "PO8", "P6", "TPP8H", "TPP10H"]),
DefinedElectrode("P10", "X", 164.2553595503051, ["PPO10H", "TPP10H"]),
DefinedElectrode("PPO9H", "Y", 175.91582637727626, ["P9", "TPP9H", "P7", "PO7", "PO9"]),
DefinedElectrode("PPO5H", "Y", 161.36813593767513, ["P5", "CPP5H", "P3", "PO3"]),
DefinedElectrode("PPO1", "X", 168.11630764741417, ["PO3", "P3", "P1", "CPP3H", "CPP1H", "PZ", "PPO2", "POZ"]),
DefinedElectrode("PPO2", "X", 170.74808035231317, ["POZ", "PPO1", "PZ", "CPP2H", "P2", "P4", "PO4"]),
DefinedElectrode("PPO6H", "Y", 171.16681554845846, ["PO4", "P4", "CPP6H", "P6", "PO8"]),
DefinedElectrode("PPO10H", "Y", 171.1889239232492, ["PO10", "PO8", "P8", "P10"]),
DefinedElectrode("PO9", "X", 181.2981798309073, ["PPO9H", "PO7", "POO9H", "I1"]),
DefinedElectrode("PO7", "G", 183.79552177895957, ["PO9", "PPO9H", "P7", "O1", "POO9H"]),
DefinedElectrode("PO3", "G", 164.27665244337066, ["P5", "PPO5H", "CPP5H", "P3", "P1", "PPO1", "POO3H"]),
DefinedElectrode("POZ", "P", 180.10830164653714, ["POO3H", "PPO1", "PZ", "PPO2", "POO4H"]),
DefinedElectrode("PO4", "G", 176.2382128427317, ["POO4H", "PPO2", "P2", "P4", "P6", "PPO6H", "PO8"]),
DefinedElectrode("PO8", "G", 179.47761382412014, ["POO10H", "O2", "PO4", "PPO6H", "P6", "P8", "PPO10H", "PO10"]),
DefinedElectrode("PO10", "X", 178.77107453947912, ["I2", "POO10H", "PO8", "PPO10H"]),
DefinedElectrode("POO9H", "Y", 176.90446684298283, ["PO9", "PO7", "O1", "OI1H", "I1"]),
DefinedElectrode("POO3H", "Y", 188.2686145909615, ["OI1H", "O1", "PO3", "POZ", "POO4H"]),
DefinedElectrode("POO4H", "Y", 187.193806842, ["POO3H", "POZ", "PO4", "O2", "OI2H"]),
DefinedElectrode("POO10H", "Y", 182.87750390083525, ["OI2H", "O2", "PO8", "PO10", "I2"]),
DefinedElectrode("O1", "P", 188.65403011862747, ["POO9H", "PO7", "POO3H", "OI1H"]),
DefinedElectrode("O2", "P", 186.68509862868004, ["OI2H", "POO4H", "PO8", "POO10H"]),
DefinedElectrode("OI1H", "Y", 187.84311922985097, ["I1", "POO9H", "O1", "POO3H", "OI2H", "IZ"]),
DefinedElectrode("OI2H", "Y", 188.39531316091703, ["IZ", "OI1H", "POO4H", "O2", "POO10H", "I2"]),
DefinedElectrode("I1", "X", 180.20496005659777, ["PO9", "POO9H", "OI1H", "IZ"]),
DefinedElectrode("IZ", "X", 187.5388339997879, ["I1", "OI1H", "OI2H"]),
DefinedElectrode("I2", "X", 181.06539696474314, ["OI2H", "POO10H", "PO10"]),



]

class DetectedElectrode:
    def __init__(self, detectedColor, detectedSequence, distToFace, neighborIndexes, position, assignedElectrodeIndex):
        self.detectedColor = detectedColor
        self.detectedSequence = detectedSequence
        self.distToFace = distToFace
        self.neighborIndexes = neighborIndexes
        self.position = position
        self.assignedElectrodeIndex = assignedElectrodeIndex

"""
detectedElectrodes = [
    DetectedElectrode("X", "", [], (405, -498), -1),   #0
DetectedElectrode("X", "GP", [7, 2], (570, -455), -1),
DetectedElectrode("P", "X", [1], (590, -443), -1),
DetectedElectrode("G", "XPPXX", [6, 11, 2, 1, 0], (481, -452), -1),
DetectedElectrode("P", "GXGXX", [5, 10, 13, 6, 0], (361, -434), -1),
DetectedElectrode("G", "PXPX", [8, 12, 16, 10], (262, -402), -1),
DetectedElectrode("X", "XGYPGXP", [10, 13, 19, 11, 3, 0, 4], (427, -391), -1),
DetectedElectrode("G", "YPXPX", [14, 17, 9, 2, 1], (593, -374), -1),
DetectedElectrode("P", "YYGX", [15, 21, 18, 12], (193, -364), -1),
DetectedElectrode("X", "YPXPG", [14, 17, 20, 2, 7], (639, -359), -1),
DetectedElectrode("X", "XPYGXPG", [12, 16, 22, 13, 6, 4, 5], (316, -363), -1), #10
DetectedElectrode("P", "GYGYGXGX", [13, 19, 24, 14, 7, 1, 3, 6], (493, -350), -1),
DetectedElectrode("X", "YYGYPXGP", [15, 21, 18, 23, 16, 10, 5, 8], (231, -342), -1),
DetectedElectrode("G", "PYPYPXPX", [16, 22, 27, 19, 11, 6, 4, 10], (384, -318), -1),
DetectedElectrode("Y", "GYGPXXGP", [24, 25, 26, 17, 20, 9, 7, 11], (564, -315), -1),
DetectedElectrode("Y", "Y", [21], (157, -304), -1),
DetectedElectrode("P", "GYGYGXGXP", [18, 23, 28, 22, 13, 10, 5, 12, 8], (276, -300), -1),
DetectedElectrode("P", "YGXXGY", [25, 26, 20, 9, 7, 14], (614, -288), -1),
DetectedElectrode("G", "YYXPY", [21, 23, 12, 8, 15], (195, -288), -1),
DetectedElectrode("Y", "YPGYGYPXG", [22, 27, 33, 29, 24, 14, 11, 6, 13], (451, -274), -1),
DetectedElectrode("X", "GXP", [26, 9, 17], (654, -268), -1), #20
DetectedElectrode("Y", "YGXPY", [23, 18, 12, 8, 15], (165, -265), -1),
DetectedElectrode("Y", "YGPYPGXP", [23, 28, 35, 32, 27, 13, 10, 16], (331, -249), -1),
DetectedElectrode("Y", "GPXGYY", [28, 16, 12, 18, 15, 21], (231, -247), -1),
DetectedElectrode("G", "YXPXYGPYPY", [29, 34, 31, 30, 25, 26, 17, 14, 11, 19], (519, -244), -1),
DetectedElectrode("Y", "PXGXPYG", [31, 30, 26, 20, 17, 14, 24], (580, -225), -1),
DetectedElectrode("G", "XXPY", [30, 20, 17, 25], (623, -221), -1),
DetectedElectrode("P", "GYPGYYGY", [28, 32, 35, 33, 29, 19, 13, 22], (398, -209), -1), #CZ
DetectedElectrode("G", "PYYPY", [35, 32, 22, 16, 23], (295, -200), -1),
DetectedElectrode("Y", "GXPGYP", [33, 34, 31, 24, 19, 27], (474, -186), -1),
DetectedElectrode("X", "Y", [25], (586, -167), -1), #30
DetectedElectrode("P", "XXYGY", [34, 30, 25, 24, 29], (539, -167), -1),
DetectedElectrode("Y", "PGPYG", [35, 33, 27, 22, 28], (363, -162), -1),
DetectedElectrode("G", "XYP", [34, 29, 27], (440, -141), -1),
DetectedElectrode("X", "PY", [31, 29], (503, -127), -1),
DetectedElectrode("P", "YG", [32, 28], (342, -127), -1), #35
]
"""
detectedElectrodes = [
DetectedElectrode("X", "PXG", 459.1394123792903, [3, 6, 2], (403, -501), -1),
DetectedElectrode("P", "GXGX", 599.0008347239593, [2, 4, 7, 8], (571, -462), -1),
DetectedElectrode("G", "PXXGPX", 511.8456798684541, [3, 6, 4, 7, 1, 0], (481, -456), -1),
DetectedElectrode("P", "GXXGX", 391.95025194532025, [5, 10, 6, 2, 0], (360, -436), -1),
DetectedElectrode("X", "XPYGXPG", 547.170905659283, [6, 11, 13, 7, 8, 1, 2], (530, -417), -1),
DetectedElectrode("G", "PXPXXP", 287.2646863086377, [9, 12, 15, 10, 6, 3], (261, -401), -1),
DetectedElectrode("X", "XGPXGXPG", 440.477014156244, [10, 14, 11, 4, 2, 0, 3, 5], (426, -393), -1),
DetectedElectrode("G", "PYPXXPGX", 603.0165835198897, [11, 13, 16, 18, 8, 1, 2, 4], (595, -379), -1),
DetectedElectrode("X", "YPXPXG", 647.6025015393316, [13, 16, 18, 1, 4, 7], (642, -366), -1),
DetectedElectrode("P", "YGPXXG", 210.23082552280482, [20, 17, 15, 12, 10, 5], (194, -362), -1),
DetectedElectrode("X", "PXGPGXPG", 326.4659247149693, [9, 12, 17, 15, 14, 6, 3, 5], (316, -363), -1), #10
DetectedElectrode("P", "GYGYGXX", 499.2193906490412, [14, 19, 21, 13, 7, 4, 6], (494, -353), -1),
DetectedElectrode("X", "YGYPXGP", 238.17010727629108, [20, 17, 23, 15, 10, 5, 9], (231, -339), -1),
DetectedElectrode("Y", "GYGXPXGXP", 568.3396871590088, [21, 24, 25, 18, 16, 8, 7, 4, 11], (567, -320), -1),
DetectedElectrode("G", "YPYPXX", 386.7738357231523, [22, 26, 19, 11, 6, 10], (385, -318), -1),
DetectedElectrode("P", "GYYGYXGXP", 277.58422145359776, [17, 20, 23, 27, 22, 10, 5, 12, 9], (277, -299), -1),
DetectedElectrode("P", "GYGXXGY", 618.1367162691438, [21, 24, 25, 18, 8, 7, 13], (618, -294), -1),
DetectedElectrode("G", "YYGYPXXP", 196.02295783912658, [20, 23, 27, 22, 15, 10, 12, 9], (196, -284), -1),
DetectedElectrode("X", "GYGXXGPY", 659.0485566329692, [21, 24, 25, 29, 8, 7, 16, 13], (659, -273), -1),
DetectedElectrode("Y", "YPGPG", 454.0275322048212, [22, 26, 21, 11, 14], (454, -276), -1),
DetectedElectrode("Y", "GYPGXP", 171.41761869772895, [27, 23, 15, 17, 12, 9], (170, -259), -1), # 20
DetectedElectrode("G", "PYPXYGXPYPY", 523.106107783115, [26, 28, 30, 29, 24, 25, 18, 16, 13, 11, 19], (522, -247), -1),
DetectedElectrode("Y", "YGYPYGPG", 334.63114021262277, [23, 27, 31, 26, 19, 14, 15, 17], (333, -248), -1),
DetectedElectrode("Y", "GYPXGY", 235.9194777885031, [27, 22, 15, 12, 17, 20], (233, -244), -1),
DetectedElectrode("Y", "YXPXGXPYG", 587.3959482325359, [28, 33, 30, 29, 25, 18, 16, 13, 21], (585, -228), -1),
DetectedElectrode("G", "YPXXPYGY", 630.4918714781342, [28, 30, 29, 18, 16, 13, 21, 24], (628, -225), -1),
DetectedElectrode("P", "GYPGYGYGY", 407.4125673073917, [27, 31, 34, 32, 28, 21, 19, 14, 22], (401, -209), -1),
DetectedElectrode("G", "PYGPYPGYY", 310.3063002905355, [34, 31, 32, 26, 22, 15, 17, 23, 20], (299, -198), -1),
DetectedElectrode("Y", "YPGXPXGYGP", 488.3298065856722, [31, 34, 32, 33, 30, 29, 25, 24, 21, 26], (479, -186), -1), # 28
DetectedElectrode("X", "PGXXGYGY", 603.2992623897364, [30, 32, 33, 18, 25, 24, 21, 28], (593, -170), -1),
DetectedElectrode("P", "GXXGYGY", 555.409758646713, [32, 33, 29, 25, 24, 21, 28], (544, -169), -1), # 30
DetectedElectrode("Y", "PGXYPYG", 386.1204475290062, [34, 32, 33, 28, 26, 22, 27], (367, -161), -1),
DetectedElectrode("G", "PXXPYPGY", 467.4569498895059, [34, 33, 29, 30, 28, 26, 27, 31], (446, -141), -1),
DetectedElectrode("X", "PXPYYYG", 532.4556319544381, [34, 29, 30, 24, 28, 31, 32], (510, -128), -1),
DetectedElectrode("P", "XGYPYG", 380.4536765494585, [33, 32, 28, 26, 31, 27], (347, -125), -1), # 34
]




def getDefinedElectrodeByName(name: str):
    for electrode in definedElectrodes:
        if electrode.name == name:
            return electrode

    return None

def getDefinedSequence(electrode: DefinedElectrode):
    if definedElectrodes[definedElectrodes.index(electrode)].sequence != None:
        return definedElectrodes[definedElectrodes.index(electrode)].sequence

    sequence = ""
    for neighbor in electrode.neighbors:
        sequence += getDefinedElectrodeByName(neighbor).color

    #print(f"Sequence for {electrode.name}: {sequence}")

    definedElectrodes[definedElectrodes.index(electrode)].sequence = sequence

    return sequence

levenshteinCache = {}

def circularLevenshtein(a, b):
    global levenshteinCache
    if (a, b) in levenshteinCache:
        return levenshteinCache[(a, b)]
    elif (b, a) in levenshteinCache:
        return levenshteinCache[(b, a)]

    print(f"Calculating distance between {a} and {b}")
    minDistance = float("inf")
    concatenated = a + a

    for i in range(len(a)):
        rotated = concatenated[i:i + len(a)]
        distance = lev.distance(rotated, b)
        if distance < minDistance:
            minDistance = distance

    levenshteinCache[(a, b)] = minDistance

    return minDistance

def amountDifference(a, b):
    shouldAmount = {}
    for char in a:
        if char not in shouldAmount:
            shouldAmount[char] = 0

        shouldAmount[char] += 1

    hasAmount = {}
    for char in b:
        if char not in hasAmount:
            hasAmount[char] = 0

        hasAmount[char] += 1

    diff = 0
    for char in shouldAmount:
        if char not in hasAmount:
            diff += shouldAmount[char]
        else:
            diff += abs(shouldAmount[char] - hasAmount[char])

    return diff

def checkTestColorSequence(testElectrode: DetectedElectrode, possibleLabels: list[str]):
    distances = []
    for defElectrode in definedElectrodes:
        if testElectrode.detectedColor != defElectrode.color:
            continue

        if defElectrode.name not in possibleLabels:
            continue

        dist = circularLevenshtein(getDefinedSequence(defElectrode), testElectrode.detectedSequence)
        distances.append({"name": defElectrode.name, "distance": dist, "sequence": getDefinedSequence(defElectrode)})

    distances.sort(key=lambda x: x["distance"])
    return distances[0] if len(distances) > 0 else None




def printState(currentElectrodeIndex):
    fig, ax = plt.subplots()

    for i, electrode in enumerate(detectedElectrodes):
        elecDef: DefinedElectrode
        if electrode.assignedElectrodeIndex == -1:
            elecDef = DefinedElectrode("", "black", [])
        else:
            elecDef = definedElectrodes[electrode.assignedElectrodeIndex]


        color = "blue"
        if electrode.detectedColor == "Y":
            color = "yellow"
        elif electrode.detectedColor == "G":
            color = "green"
        elif electrode.detectedColor == "P":
            color = "purple"

        if electrode == detectedElectrodes[currentElectrodeIndex]:
            color = "red"

        ax.scatter(electrode.position[0], electrode.position[1], color=color)
        ax.annotate(str(i) + ": " + elecDef.name, (electrode.position[0], electrode.position[1]))

        if electrode == detectedElectrodes[currentElectrodeIndex]:
            for neighborIdx in electrode.neighborIndexes:
                neighbor = detectedElectrodes[neighborIdx]
                plt.plot([electrode.position[0], neighbor.position[0]], [electrode.position[1], neighbor.position[1]], color="black")

    plt.show(block=False)
    fig.waitforbuttonpress()
    print("Press any key to continue")
    plt.close()




fig, ax = plt.subplots()

for i, electrode in enumerate(detectedElectrodes):
    elecDef: DefinedElectrode
    if electrode.assignedElectrodeIndex == -1:
        elecDef = DefinedElectrode("", "black", 0, [])
    else:
        elecDef = definedElectrodes[electrode.assignedElectrodeIndex]


    color = "blue"
    if electrode.detectedColor == "Y":
        color = "yellow"
    elif electrode.detectedColor == "G":
        color = "green"
    elif electrode.detectedColor == "P":
        color = "purple"

    ax.scatter(electrode.position[0], electrode.position[1], color=color)
    ax.annotate(str(i) + ": " + elecDef.name, (electrode.position[0], electrode.position[1]))

plt.show()

interestingElectrodes = [
    "F3", "F1", "FFC3H", "FC3", "FFC1H", "FC1", "FCC3H", "C3", "FCZ", "FCC1H", "C1", "CCP3H", "CP3", "FC2", "FCC2H", "CZ", "CCP1H", "CP1", "C2", "CCP2H", "CPZ", "CPP1H", "P1"
, "CCP4H", "CP2", "CPP2H", "PZ", "PPO1", "CPP4H", "P2", "PPO2"]

interestingElectrodes = [
    "AFF5H", "AFF1", "AFF2", "F7", "F5", "F3", "F1", "FZ", "F2", "FFT7H", "FFC5H", "FFC3H", "FFC1H", "FFC2H", "FFC4H", "FT9", "FT7", "FC5", "FC3", "FC1", "FCZ", "FC2", "FTT9H", "FTT7H", "FCC5H", "FCC3H", "FCC1H", "FCC2H", "FCC4H", "T7", "C5", "C3", "C1", "CZ", "C2", "TTP7H", "CCP5H", "CCP3H", "CCP1H", "CCP2H", "CCP4H", "M2", "TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "TPP9H", "TPP7H", "CPP5H", "CPP3H", "CPP1H", "CPP2H", "CPP4H", "P9", "P7", "P5", "P3", "P1", "PZ", "P2", "PPO9H", "PPO5H", "PPO1", "PPO2", "PO9", "PO7", "PO3", "POZ", "PO4", "POO9H", "POO3H", "POO4H", "O1", "O2", "OI1H", "OI2H", "I1", "IZ", "I2"
]

interestingElectrodes = [
    "AFF2", "F3", "F1", "F2", "FFC3H", "FFC1H", "FFC2H", "FFC4H", "FC3", "FC1", "FCZ", "FCC3H", "FCC1H", "FCC2H", "C3", "C1", "CZ", "C2", "CCP3H", "CCP1H", "CCP2H", "CCP4H", "CP3", "CP1", "CPZ", "CP2", "CPP3H", "CPP1H", "CPP2H", "CPP4H", "P3", "P1", "PZ", "P2", "PPO1", "PPO2", "PO3", "POZ", "PO4", "POO3H", "POO4H", "O1", "O2", "OI1H", "OI2H", "I1", "IZ", "I2"
]

### Normalize DistanceToFace for defined Electrodes
maxDist = max([x.distToFace for x in definedElectrodes])
minDist = min([x.distToFace for x in definedElectrodes])
for electrode in definedElectrodes:
    electrode.distToFace = (electrode.distToFace - minDist) / (maxDist - minDist)

### Normalize DistanceToFace for detected Electrodes
maxDist = max([x.distToFace for x in detectedElectrodes])
minDist = min([x.distToFace for x in detectedElectrodes])
for electrode in detectedElectrodes:
    electrode.distToFace = (electrode.distToFace - minDist) / (maxDist - minDist)









minimumAssignment = 8# len(interestingElectrodes) * 0.7 #len(detectedElectrodes) * 0.5


def checkAssignmentSolution(assignments: dict[int, int]):
    #print("Checking Assignment: ", assignments)

    # Check if all detected Electrodes got labeled
    if len(assignments) < minimumAssignment:
        return False

    for eIdx in assignments:
        dElectrode = detectedElectrodes[eIdx]
        pElectrode = definedElectrodes[assignments[eIdx]]

        # Check if each electrode has its color
        if dElectrode.detectedColor != pElectrode.color:
            return False

        # Check if each electrode can be that label according to it's neighbors
        wrongNeighbors = 0
        for neighborIdx in dElectrode.neighborIndexes:
            if neighborIdx in assignments:
                if pElectrode.name not in definedElectrodes[assignments[neighborIdx]].neighbors:
                    wrongNeighbors += 1

        if wrongNeighbors >= 1:
            return False

    return True


# Backtracking Algorithm
def algorithm(assignments: dict[int, int], currentIndex: int, checkAmount: int = 0):
    checkAmount += 1
    if checkAmount % 10000 == 0:
        print("Checked " + str(checkAmount) + " Assignments so far. Currently at Index: " + str(currentIndex) + " with " + str(len(assignments)) + " Assignments")

    if len(assignments) >= minimumAssignment and checkAssignmentSolution(assignments): ##
        return True, assignments, checkAmount

    if len(assignments) == len(detectedElectrodes):
        return False, None, checkAmount

    #if len(assignments) >= minimumAssignment:
    #    return False, None, checkAmount

    currentElectrode = detectedElectrodes[currentIndex]

    # Get next Electrode

    nextElectrodeIndex = -1

    # All current unassigned neighbors
    neighborsIdxs = [x for x in currentElectrode.neighborIndexes if x not in assignments]
    neighbors = [detectedElectrodes[x] for x in neighborsIdxs]

    # Sort by amount of neighbors of those neighbors
    neighbors.sort(key=lambda x: len([n for n in x.neighborIndexes if n in assignments]), reverse=True)

    if len(neighbors) < 1 or len(neighbors[0].neighborIndexes) < 4:
        return False, None, checkAmount

    nextElectrodeIndex = detectedElectrodes.index(neighbors[0])


    #for neighborIdx in currentElectrode.neighborIndexes:
    #    if neighborIdx not in newAssignments:
    #        nextElectrodeIndex = neighborIdx
    #        break

    if nextElectrodeIndex == -1:
        for i in range(len(detectedElectrodes)):
            if i not in assignments:
                nextElectrodeIndex = i
                break


        #nextElectrodeIndex = customTraverseOrder.index(currentIndex) + 1








    newAssignments = assignments.copy()
    possibleChoices = definedElectrodes.copy()

    # Filter Choices for interesting Electrodes
    #print("Start: " + str(len(possibleChoices)))
    possibleChoices = [x for x in possibleChoices if x.name in interestingElectrodes]
    #print("Interesting: " + str(len(possibleChoices)))

    # Filter for Colors
    possibleChoices = [x for x in possibleChoices if x.color == currentElectrode.detectedColor]
    #print("Color: " + str(len(possibleChoices)))

    # Filter for already assigned
    possibleChoices = [x for x in possibleChoices if definedElectrodes.index(x) not in [assignments[x] for x in assignments]]
    #print("Assigned: " + str(len(possibleChoices)))

    # Filter for Distance to Face
    possibleChoices = [x for x in possibleChoices if abs(x.distToFace - currentElectrode.distToFace) < 0.2]
    #print("Distance: " + str(len(possibleChoices)))

    #print("possible1: ", [x.name for x in possibleChoices])
    # Filter for possible Neighbors
    assignedNeighbors = [x for x in currentElectrode.neighborIndexes if x in assignments]
    if len(assignedNeighbors) > 0:
        possibleNeighboring = set()
        for neighborIdx in assignedNeighbors:
            neighbor = definedElectrodes[assignments[neighborIdx]]
            possibleNeighboring.update(neighbor.neighbors)

        pass
        possibleChoices = [x for x in possibleChoices if x.name in possibleNeighboring]

    #print("Neighbors: " + str(len(possibleChoices)))

    # Filter for Sequence
    #currentSequence = currentElectrode.detectedSequence
    #possibleChoices = [x for x in possibleChoices if circularLevenshtein(currentSequence, getDefinedSequence(x)) <= 4]
    #print("Sequence: " + str(len(possibleChoices)))


    #print("Checking " + str(len(possibleChoices)) + " choices for " + str(currentIndex) + " (" + str(checkAmount) +" Checks so far)")
#    print("Possible Choices: ", [x.name for x in possibleChoices])
    pass
    # Check Choices
    for possibleLabel in [x.name for x in possibleChoices]:
        # Set next Choice
        newAssignments[currentIndex] = definedElectrodes.index(getDefinedElectrodeByName(possibleLabel))

        result, solution, checkAmount = algorithm(newAssignments, nextElectrodeIndex, checkAmount)# currentIndex + 1) #nextNeighbor)

        if result:
            return True, solution, checkAmount

    return False, None, checkAmount

startTime = time.time()
#success, result, checkAmount = algorithm({27: 56, 13: 55, 11: 74}, 19)
#success, result, checkAmount = algorithm({28: 56}, 22)
success, result, checkAmount = algorithm({26: 56, 31: 47, 28: 66, 22: 46, 19: 65}, 21)
#success, result, checkAmount = algorithm({}, 26)
#success, result, checkAmount = algorithm({26: 56, 31: 47, 27: 36, 22: 46}, 19)
#print("Starting with Electrode " + str(customTraverseOrder[0]))
#success, result, checkAmount = algorithm({}, customTraverseOrder[0])
endTime = time.time()

print("Time: ", endTime - startTime)

if success:
    print("Success (Checked: ", checkAmount, " assignments)")

    fig, ax = plt.subplots()
    for eIdx, detected in enumerate(detectedElectrodes):
        defined = None
        if eIdx in result:
            defined = definedElectrodes[result[eIdx]]

        color = "blue"
        if detected.detectedColor == "Y":
            color = "yellow"
        elif detected.detectedColor == "G":
            color = "green"
        elif detected.detectedColor == "P":
            color = "purple"

        ax.scatter(detected.position[0], detected.position[1], color=color)
        if defined is not None:
            #ax.annotate(str(eIdx) + ": " + defined.name, (detected.position[0], detected.position[1]))
            ax.annotate(defined.name, (detected.position[0], detected.position[1]))

    plt.axis('off')

    plt.show()

else:
    print("No Solution (Checked ", checkAmount, " assignments)")



# Show Points with labels in graph

fig, ax = plt.subplots()

for i, electrode in enumerate(detectedElectrodes):
    elecDef: DefinedElectrode
    if electrode.assignedElectrodeIndex == -1:
        elecDef = DefinedElectrode("", "black", 0, [])
    else:
        elecDef = definedElectrodes[electrode.assignedElectrodeIndex]


    color = "blue"
    if electrode.detectedColor == "Y":
        color = "yellow"
    elif electrode.detectedColor == "G":
        color = "green"
    elif electrode.detectedColor == "P":
        color = "purple"

    ax.scatter(electrode.position[0], electrode.position[1], color=color)
    ax.annotate(str(i) + ": " + elecDef.name, (electrode.position[0], electrode.position[1]))

plt.show()
