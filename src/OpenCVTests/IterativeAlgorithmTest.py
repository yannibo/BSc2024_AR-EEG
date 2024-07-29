import Levenshtein as lev
import matplotlib.pyplot as plt
import time
import math

class DefinedElectrode:
    def __init__(self, name, color, distToFace, neighbors):
        self.name = name
        self.color = color
        self.distToFace = distToFace
        self.neighbors = neighbors
        self.sequence = None

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
    DefinedElectrode("AFF5H", "Y", 60.947663819050526, ["FFC5H", "F5", "AF7", "AF3", "F3"]), #10
    DefinedElectrode("AFF1", "X", 26.481548463033654, ["F1", "AF3", "AFZ", "AFF2", "FZ", "FFC1H"]),
    DefinedElectrode("AFF2", "X", 27.95583139525634, ["FZ", "AFF1", "AFZ", "AF4", "F2", "FFC2H"]),
    DefinedElectrode("AFF6H", "Y", 71.18914423562065, ["F4", "AF4", "AF8", "F8", "F6", "FFC6H"]),
    DefinedElectrode("F7", "P", 84.64278426422419, ["AF7", "F5", "FFT7H"]),
    DefinedElectrode("F5", "G", 75.62924667745938, ["FC5", "FFT7H", "F7", "AF7", "AFF5H", "F3", "FFC5H"]),
    DefinedElectrode("F3", "P", 60.782278601579264, ["FC3", "FFC5H", "F5", "AFF5H", "AF3", "F1", "FFC3H"]),
    DefinedElectrode("F1", "G", 41.01756659042563, ["FFC3H", "F3", "AF3", "AFF1", "FZ", "FFC1H", "FC1"]),
    DefinedElectrode("FZ", "P", 29.92084632827087, ["FFC1H", "F1", "AFF1", "AFZ", "AFF2", "F2", "FFC2H", "FCZ"]),
    DefinedElectrode("F2", "G", 45.82700619721957, ["FFC2H", "FZ", "AFF2", "AF4", "F4", "FFC4H", "FC2"]),
    DefinedElectrode("F4", "P", 63.56717152744804, ["FFC4H", "FC2", "F2", "AF4", "AFF6H", "F6", "FFC6H", "FC4"]),#20
    DefinedElectrode("F6", "G", 83.0292282271731, ["FFC6H", "F4", "AFF6H", "F8", "FFT8H", "FC6"]),
    DefinedElectrode("F8", "P", 88.8120979371617, ["F6", "AFF6H", "AF8", "FT8", "FFT8H"]),
    DefinedElectrode("FFT7H", "Y", 90.45628516029166, ["FT7", "F7", "F5", "FFC5H", "FC5"]),
    DefinedElectrode("FFC5H", "X", 80.59598159958101, ["FCC5H", "FC5", "FFT7H", "F5", "AFF5H", "F3", "FFC3H", "FC3"]),
    DefinedElectrode("FFC3H", "X", 64.64247003325292, ["FC3", "FFC5H", "F3", "F1", "FFC1H", "FC1", "FCC3H"]),
    DefinedElectrode("FFC1H", "Y", 45.43635119593122, ["FC1", "FFC3H", "F1", "AFF1", "FZ", "FFC2H", "FCZ", "FCC1H"]),
    DefinedElectrode("FFC2H", "Y", 45.866557402970635, ["FCZ", "FFC1H", "FZ", "AFF2", "F2", "FFC4H", "FC2", "FCC2H"]),
    DefinedElectrode("FFC4H", "X", 68.77343711055892, ["FC2", "FFC2H", "F2", "F4", "FFC6H", "FC4", "FCC4H"]),
    DefinedElectrode("FFC6H", "X", 82.63723156059864, ["FC4", "FFC4H", "F4", "AFF6H", "F6", "FC6", "FCC6H"]),
    DefinedElectrode("FFT8H", "Y", 101.79505592119885, ["FC6", "F6", "F8", "FT8", "FTT8H"]),#30
    DefinedElectrode("FT9", "X", 106.28148614881145, ["FTT9H"]),
    DefinedElectrode("FT7", "G", 109.95648150973183, ["T7", "FTT9H", "FFT7H", "FC5", "FTT7H"]),
    DefinedElectrode("FC5", "P", 103.22708158714941, ["FTT7H", "FT7", "FFT7H", "F5", "FFC5H", "FC3", "FCC5H", "C5"]),
    DefinedElectrode("FC3", "G", 85.66534408382424, ["FCC5H", "FC5", "FFC5H", "F3", "FFC3H", "FC1", "FCC3H", "C3"]),
    DefinedElectrode("FC1", "P", 67.3849836462101, ["FCC3H", "FC3", "FFC3H", "F1", "FFC1H", "FCZ", "FCC1H", "C1"]),
    DefinedElectrode("FCZ", "G", 56.67272911198119, ["FCC1H", "FC1", "FFC1H", "FZ", "FFC2H", "FC2", "FCC2H", "CZ"]),
    DefinedElectrode("FC2", "P", 70.18002325448461, ["FCC2H", "FCZ", "FFC2H", "F2", "F4", "FFC4H", "FC4", "FCC4H", "C2"]),
    DefinedElectrode("FC4", "G", 87.69604362797675, ["FCC4H", "FC2", "FFC4H", "F4", "FFC6H", "FC6", "FCC6H", "C4"]),
    DefinedElectrode("FC6", "P", 103.08953460463384, ["FCC6H", "FC4", "FFC6H", "F6", "FFT8H", "FT8", "FTT8H"]),
    DefinedElectrode("FT8", "G", 106.4518249960986, ["FTT8H", "FC6", "FFT8H", "F8", "FTT10H"]),#40
    DefinedElectrode("FT10", "X", 104.94261171230684, ["FTT10H", "M1"]),
    DefinedElectrode("FTT9H", "Y", 118.63593186298999, ["FT9", "FT7", "FTT7H", "T7"]),
    DefinedElectrode("FTT7H", "Y", 119.28461441443321, ["T7", "FTT9H", "FT7", "FC5", "FCC5H", "C5"]),
    DefinedElectrode("FCC5H", "X", 108.61604416475497, ["C5", "FTT7H", "FC5", "FFC5H", "FC3", "FCC3H", "C3", "CCP5H"]),
    DefinedElectrode("FCC3H", "X", 92.09616728724384, ["C3", "FCC5H", "FC3", "FFC3H", "FC1", "FCC1H", "C1", "CCP3H"]),
    DefinedElectrode("FCC1H", "Y", 79.5496400808954, ["C1", "FCC3H", "FC1", "FFC1H", "FCZ", "FCC2H", "CZ", "CCP1H"]),
    DefinedElectrode("FCC2H", "Y", 77.18142021238013, ["CZ", "FCC1H", "FCZ", "FFC2H", "FC2", "FCC4H", "C2", "CCP2H"]),
    DefinedElectrode("FCC4H", "X", 95.81809729899672, ["C2", "FCC2H", "FC2", "FFC4H", "FC4", "FCC6H", "C4", "CCP4H"]),
    DefinedElectrode("FCC6H", "X", 111.0333360977684, ["C4", "FCC4H", "FC4", "FFC6H", "FC6", "FTT8H", "C6", "CCP6H"]),
    DefinedElectrode("FTT8H", "Y", 119.26278931837876, ["C6", "FCC6H", "FC6", "FFT8H", "FT8", "T8"]),#50
    DefinedElectrode("FTT10H", "Y", 119.16547196650548, ["T8", "FT8", "FT10"]),
    DefinedElectrode("T7", "P", 132.27013060400296, ["FTT9H", "FT7", "FTT7H", "TTP7H", "TP7"]),
    DefinedElectrode("C5", "G", 129.4576837310169, ["TTP7H", "FTT7H", "FC5", "FCC5H", "C3", "CCP5H", "CP5"]),
    DefinedElectrode("C3", "P", 113.64337231884666, ["CCP5H", "C5", "FCC5H", "FC3", "FCC3H", "C1", "CCP3H", "CP3"]),
    DefinedElectrode("C1", "G", 100.11200083906026, ["CCP3H", "C3", "FCC3H", "FC1", "FCC1H", "CZ", "CCP1H", "CP1"]),
    DefinedElectrode("CZ", "P", 92.35408653654693, ["CCP1H", "C1", "FCC1H", "FCZ", "FCC2H", "C2", "CCP2H", "CPZ"]),
    DefinedElectrode("C2", "G", 101.38963432718357, ["CCP2H", "CZ", "FCC2H", "FC2", "FCC4H", "C4", "CCP4H", "CP2"]),
    DefinedElectrode("C4", "P", 117.09130092368092, ["CCP4H", "C2", "FCC4H", "FC4", "FCC6H", "C6", "CCP6H", "CP4"]),
    DefinedElectrode("C6", "G", 129.70056515682575, ["CCP6H", "C4", "FCC6H", "FTT8H", "TTP8H", "CP6"]),
    DefinedElectrode("T8", "P", 132.52633902737978, ["TP8", "TTP8H", "FTT8H", "FTT10H"]),#60
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
        self.normalizedPos = None

detectedElectrodes = [
    DetectedElectrode("G", "YX", 489.979591411724, [4, 1], (488, -325), -1),
    DetectedElectrode("X", "GXGG", 566.7944953861144, [9, 6, 3, 0], (566, -311), -1),
    DetectedElectrode("Y", "", 106.90182411914213, [], (102, -313), -1),
    DetectedElectrode("G", "XXPX", 659.4368809825547, [6, 8, 5, 1], (659, -305), -1),
    DetectedElectrode("Y", "XXG", 421.34309060431974, [11, 10, 0], (421, -298), -1),
    DetectedElectrode("P", "XXGG", 750.0326659552902, [8, 12, 7, 3], (750, -288), -1),
    DetectedElectrode("X", "XGPXGX", 613.1174438881999, [10, 9, 13, 8, 3, 1], (613, -269), -1),
    DetectedElectrode("G", "XXP", 825.2672294475287, [8, 12, 5], (825, -260), -1),
    DetectedElectrode("X", "PGXGPGX", 704.7730131042192, [13, 15, 12, 7, 5, 3, 6], (704, -248), -1),
    DetectedElectrode("G", "XXPYPXX", 542.3329235810786, [11, 10, 17, 14, 13, 6, 1], (541, -243), -1),
    DetectedElectrode("X", "XPYGXY", 486.90245429654595, [11, 17, 14, 9, 6, 4], (485, -238), -1), # 10
    DetectedElectrode("X", "XPXGY", 428.58488074125995, [18, 17, 10, 9, 4], (426, -234), -1),
    DetectedElectrode("X", "GPGPX", 787.7182237323192, [15, 16, 7, 5, 8], (786, -229), -1),
    DetectedElectrode("P", "YYGXXG", 647.4758682761852, [14, 19, 15, 8, 6, 9], (644, -214), -1),
    DetectedElectrode("Y", "PXYGYPGX", 569.9912280026773, [17, 18, 23, 22, 19, 13, 9, 10], (563, -192), -1),
    DetectedElectrode("G", "YYYPXXP", 745.0812036281683, [19, 21, 20, 16, 12, 8, 13], (739, -186), -1),
    DetectedElectrode("P", "YYXG", 816.5225042826438, [21, 20, 12, 15], (810, -178), -1),
    DetectedElectrode("P", "XGYGYGXX", 506.01383380299, [18, 24, 23, 22, 14, 9, 10, 11], (495, -176), -1),
    DetectedElectrode("X", "GYYPX", 468.96588362054655, [24, 23, 14, 17, 11], (452, -156), -1),
    DetectedElectrode("Y", "GYPYGPY", 677.5876327088622, [22, 27, 25, 21, 15, 13, 14], (665, -151), -1),
    DetectedElectrode("Y", "YGPG", 838.1700304830757, [21, 26, 16, 15], (825, -133), -1), # 20
    DetectedElectrode("Y", "PYGYPGY", 775.449547037072, [25, 28, 26, 20, 16, 15, 19], (761, -132), -1),
    DetectedElectrode("G", "GYPYPYYP", 617.5111335028705, [24, 23, 30, 27, 25, 19, 14, 17], (598, -127), -1),
    DetectedElectrode("Y", "GXPYGYPX", 553.7806424930362, [24, 29, 30, 27, 22, 14, 17, 18], (528, -114), -1),
    DetectedElectrode("G", "XPYGPX", 512.4451190127583, [29, 30, 23, 22, 17, 18], (482, -107), -1),
    DetectedElectrode("P", "YGXYGYYG", 713.8550272989607, [27, 31, 32, 28, 26, 21, 19, 22], (690, -98), -1), # 25
    DetectedElectrode("G", "YXYYP", 798.6845434838464, [28, 32, 20, 21, 25], (776, -92), -1),
    DetectedElectrode("Y", "XPGXYPYGY", 660.2863015389612, [29, 30, 31, 32, 28, 25, 19, 22, 23], (627, -74), -1),
    DetectedElectrode("Y", "GXGYPY", 752.4925248798156, [31, 32, 26, 21, 25, 27], (719, -59), -1),
    DetectedElectrode("X", "PYYG", 562.406436663024, [30, 27, 23, 24], (515, -55), -1),
    DetectedElectrode("P", "XGYGYG", 608.7133972568699, [29, 31, 27, 22, 23, 24], (566, -57), -1),
    DetectedElectrode("G", "XYPYP", 702.1317540177199, [32, 28, 25, 27, 30], (658, -36), -1),
    DetectedElectrode("X", "GYPYG", 767.5135177962666, [26, 28, 25, 27, 31], (726, -32), -1),
]


""" DetectedElectrode("X", "PXG", 459.1394123792903, [3, 6, 2], (403, -501), -1),
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
DetectedElectrode("P", "GYPGYGYGY", 407.4125673073917, [27, 31, 32, 28, 21, 19, 14, 22], (401, -209), -1), # 26
DetectedElectrode("G", "PYGPYPGYY", 310.3063002905355, [34, 31, 32, 26, 22, 15, 17, 23, 20], (299, -198), -1),
DetectedElectrode("Y", "YPGXPXGYGP", 488.3298065856722, [31, 34, 32, 33, 30, 29, 25, 24, 21, 26], (479, -186), -1), # 28
DetectedElectrode("X", "PGXXGYGY", 603.2992623897364, [30, 32, 33, 18, 25, 24, 21, 28], (593, -170), -1),
DetectedElectrode("P", "GXXGYGY", 555.409758646713, [32, 33, 29, 25, 24, 21, 28], (544, -169), -1), # 30
DetectedElectrode("Y", "PGXYPYG", 386.1204475290062, [34, 32, 33, 28, 26, 22, 27], (367, -161), -1),
DetectedElectrode("G", "PXXPYPGY", 467.4569498895059, [34, 33, 29, 30, 28, 26, 27, 31], (446, -141), -1),
DetectedElectrode("X", "PXPYYYG", 532.4556319544381, [34, 29, 30, 24, 28, 31, 32], (510, -128), -1),
DetectedElectrode("P", "XGYPYG", 380.4536765494585, [33, 32, 28, 31, 27], (347, -125), -1), # 34 """


class VirtualElectrode:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos
        self.normalizedPos = None

virtualElectrodes = [
    VirtualElectrode("FP1", (297.8344,-501.5272)),
    VirtualElectrode("FPZ", (321.2947,-535.6448)),
    VirtualElectrode("FP2", (364.6418,-577.9304)),
    VirtualElectrode("AFP3H", (301.2858,-535.4391)),
    VirtualElectrode("AFP4H", (335.8759,-578.2615)),
    VirtualElectrode("AF7", (292.2781,-431.894)),
    VirtualElectrode("AF3", (290.3954,-506.9324)),
    VirtualElectrode("AFZ", (320.5386,-572.4434)),
    VirtualElectrode("AF4", (381.2256,-611.8435)),
    VirtualElectrode("AF8", (415.2167,-589.8519)),
    VirtualElectrode("AFF5H", (294.9067,-464.6453)),
    VirtualElectrode("AFF1", (316.3557,-555.7444)),
    VirtualElectrode("AFF2", (354.1743,-603.2584)),
    VirtualElectrode("AFF6H", (429.3928,-619.7231)),
    VirtualElectrode("F7", (317.7779,-394.4378)),
    VirtualElectrode("F5", (304.9079,-430.1519)),
    VirtualElectrode("F3", (308.74,-485.4653)),
    VirtualElectrode("F1", (323.4746,-541.0545)),
    VirtualElectrode("FZ", (348.36,-588.4079)),
    VirtualElectrode("F2", (388.4304,-622.0522)),
    VirtualElectrode("F4", (421.7453,-630.4656)),
    VirtualElectrode("F6", (452.9292,-619.3323)),
    VirtualElectrode("F8", (466.2285,-588.6663)),
    VirtualElectrode("FFT7H", (324.1233,-393.5004)),
    VirtualElectrode("FFC5H", (319.4165,-439.2922)),
    VirtualElectrode("FFC3H", (334.3303,-503.4175)),
    VirtualElectrode("FFC1H", (355.3051,-566.2518)),
    VirtualElectrode("FFC2H", (385.8348,-609.6278)),
    VirtualElectrode("FFC4H", (435.4531,-634.626)),
    VirtualElectrode("FFC6H", (459.7159,-628.7413)),
    VirtualElectrode("FFT8H", (487.2569,-591.4147)),
    VirtualElectrode("FT9", (367.6513,-336.5532)),
    VirtualElectrode("FT7", (363.5662,-351.5355)),
    VirtualElectrode("FC5", (345.9715,-386.2419)),
    VirtualElectrode("FC3", (351.0504,-458.3569)),
    VirtualElectrode("FC1", (370.0986,-530.005)),
    VirtualElectrode("FCZ", (397.0989,-591.6011)),
    VirtualElectrode("FC2", (440.0802,-626.7726)),
    VirtualElectrode("FC4", (475.65,-638.2514)),
    VirtualElectrode("FC6", (500.0722,-611.9794)),
    VirtualElectrode("FT8", (505.7127,-565.7356)),
    VirtualElectrode("FTT9H", (385.7622,-333.0924)),
    VirtualElectrode("FTT7H", (378.4273,-350.963)),
    VirtualElectrode("FCC5H", (372.8176,-399.6595)),
    VirtualElectrode("FCC3H", (390.9732,-478.1211)),
    VirtualElectrode("FCC1H", (422.7074,-552.4769)),
    VirtualElectrode("FCC2H", (451.4505,-609.565)),
    VirtualElectrode("FCC4H", (497.1294,-632.8022)),
    VirtualElectrode("FCC6H", (522.9106,-626.1447)),
    VirtualElectrode("FTT8H", (531.7921,-583.6695)),
    VirtualElectrode("T7", (410.6141,-322.5868)),
    VirtualElectrode("C5", (403.6805,-352.4971)),
    VirtualElectrode("C3", (410.3454,-423.4992)),
    VirtualElectrode("C1", (441.8059,-504.0299)),
    VirtualElectrode("CZ", (469.3468,-571.8372)),
    VirtualElectrode("C2", (509.209,-616.4278)),
    VirtualElectrode("C4", (542.5735,-625.5334)),
    VirtualElectrode("C6", (555.8847,-595.4609)),
    VirtualElectrode("T8", (553.105,-548.3408)),
    VirtualElectrode("M1", (451.5148,-292.1441)),
    VirtualElectrode("TTP7H", (444.527,-321.9294)),
    VirtualElectrode("CCP5H", (437.3814,-368.5182)),
    VirtualElectrode("CCP3H", (464.5342,-452.0239)),
    VirtualElectrode("CCP1H", (500.8182,-520.6281)),
    VirtualElectrode("CCP2H", (527.7505,-577.3799)),
    VirtualElectrode("CCP4H", (561.0018,-607.6716)),
    VirtualElectrode("CCP6H", (579.6838,-602.0054)),
    VirtualElectrode("TTP8H", (575.3281,-558.4571)),
    VirtualElectrode("TP7", (461.4911,-305.29)),
    VirtualElectrode("CP5", (468.7357,-327.3352)),
    VirtualElectrode("CP3", (486.0921,-390.113)),
    VirtualElectrode("CP1", (516.5289,-463.4195)),
    VirtualElectrode("CPZ", (551.1831,-528.9262)),
    VirtualElectrode("CP2", (582.1672,-580.386)),
    VirtualElectrode("CP4", (599.0284,-592.6832)),
    VirtualElectrode("CP6", (600.4426,-568.6294)),
    VirtualElectrode("TP8", (587.1985,-530.7287)),
    VirtualElectrode("TPP9H", (498.1629,-293.0698)),
    VirtualElectrode("TPP7H", (497.856,-302.323)),
    VirtualElectrode("CPP5H", (516.2944,-342.8667)),
    VirtualElectrode("CPP3H", (533.6163,-417.2026)),
    VirtualElectrode("CPP1H", (574.9813,-474.4699)),
    VirtualElectrode("CPP2H", (601.7726,-526.4198)),
    VirtualElectrode("CPP4H", (619.4371,-564.3801)),
    VirtualElectrode("CPP6H", (628.6467,-558.4094)),
    VirtualElectrode("TPP8H", (613.4397,-531.6315)),
    VirtualElectrode("TPP10H", (611.5319,-496.3745)),
    VirtualElectrode("P9", (502.9207,-277.6714)),
    VirtualElectrode("P7", (519.7197,-297.7608)),
    VirtualElectrode("P5", (532.9788,-318.5504)),
    VirtualElectrode("P3", (554.0988,-361.7107)),
    VirtualElectrode("P1", (583.146,-418.0489)),
    VirtualElectrode("PZ", (615.0291,-475.6427)),
    VirtualElectrode("P2", (629.8898,-520.739)),
    VirtualElectrode("P4", (645.8367,-534.7851)),
    VirtualElectrode("P6", (640.9579,-522.7941)),
    VirtualElectrode("P8", (626.9943,-498.0514)),
    VirtualElectrode("P10", (628.827,-471.9055)),
    VirtualElectrode("PPO9H", (524.0002,-287.4474)),
    VirtualElectrode("PPO5H", (557.1058,-338.2709)),
    VirtualElectrode("PPO1", (614.8876,-424.299)),
    VirtualElectrode("PPO2", (642.9012,-477.4845)),
    VirtualElectrode("PPO6H", (651.0988,-504.1927)),
    VirtualElectrode("PPO10H", (634.2034,-472.9503)),
    VirtualElectrode("PO9", (572.3248,-297.547)),
    VirtualElectrode("PO7", (571.8271,-308.304)),
    VirtualElectrode("PO5", (580.7581,-318.4279)),
    VirtualElectrode("PO3", (586.2762,-359.5408)),
    VirtualElectrode("POZ", (647.1682,-420.2063)),
    VirtualElectrode("PO4", (656.496,-482.4163)),
    VirtualElectrode("PO6", (656.8195,-479.4566)),
    VirtualElectrode("PO8", (651.4924,-466.7182)),
    VirtualElectrode("PO10", (646.7024,-444.8656)),
    VirtualElectrode("POO9H", (590.2237,-318.122)),
    VirtualElectrode("POO3H", (621.6753,-369.3992)),
    VirtualElectrode("POO4H", (652.5627,-420.3881)),
    VirtualElectrode("POO10H", (654.459,-418.5822)),
    VirtualElectrode("O1", (610.2561,-337.1266)),
    VirtualElectrode("OZ", (640.764,-377.3032)),
    VirtualElectrode("O2", (654.2103,-419.3512)),
    VirtualElectrode("OI1H", (620.7706,-347.8293)),
    VirtualElectrode("OI2H", (645.0312,-385.7151)),
    VirtualElectrode("I1", (594.5569,-316.3683)),
    VirtualElectrode("IZ", (621.309,-351.3687)),
    VirtualElectrode("I2", (644.7138,-402.1863)),
]



def getDefinedElectrodeByName(name: str):
    for electrode in definedElectrodes:
        if electrode.name == name:
            return electrode

    return None


def getVirtualElectrodeByName(name: str):
    for electrode in virtualElectrodes:
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

    #print(f"Calculating distance between {a} and {b}")
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




def printState(allPossibilities: dict[int, list[int]]):
    fig, ax = plt.subplots()

    for i, electrode in enumerate(detectedElectrodes):
        ePoss = [definedElectrodes[i] for i in allPossibilities[i]]

        possStr = "\n".join([x.name for x in ePoss])

        color = "blue"
        if electrode.detectedColor == "Y":
            color = "yellow"
        elif electrode.detectedColor == "G":
            color = "green"
        elif electrode.detectedColor == "P":
            color = "purple"

        ax.scatter(electrode.position[0], electrode.position[1], color=color)
        #ax.annotate(str(i) + "\n" + possStr, (electrode.position[0], electrode.position[1]))
        ax.annotate(possStr, (electrode.position[0], electrode.position[1]))

        #if electrode == detectedElectrodes[currentElectrodeIndex]:
        #    for neighborIdx in electrode.neighborIndexes:
        #        neighbor = detectedElectrodes[neighborIdx]
        #        plt.plot([electrode.position[0], neighbor.position[0]], [electrode.position[1], neighbor.position[1]], color="black")


    plt.axis('off')
    plt.show(block=False)
    fig.waitforbuttonpress()
    print("Press any key to continue")
    plt.close()


interestingElectrodes = [
    "F3", "F1", "FFC3H", "FC3", "FFC1H", "FC1", "FCC3H", "C3", "FCZ", "FCC1H", "C1", "CCP3H", "CP3", "FC2", "FCC2H", "CZ", "CCP1H", "CP1", "C2", "CCP2H", "CPZ", "CPP1H", "P1"
, "CCP4H", "CP2", "CPP2H", "PZ", "PPO1", "CPP4H", "P2", "PPO2"]

interestingElectrodes = [
    "AFF5H", "AFF1", "AFF2", "F7", "F5", "F3", "F1", "FZ", "F2", "FFT7H", "FFC5H", "FFC3H", "FFC1H", "FFC2H", "FFC4H", "FT9", "FT7", "FC5", "FC3", "FC1", "FCZ", "FC2", "FTT9H", "FTT7H", "FCC5H", "FCC3H", "FCC1H", "FCC2H", "FCC4H", "T7", "C5", "C3", "C1", "CZ", "C2", "TTP7H", "CCP5H", "CCP3H", "CCP1H", "CCP2H", "CCP4H", "M2", "TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "TPP9H", "TPP7H", "CPP5H", "CPP3H", "CPP1H", "CPP2H", "CPP4H", "P9", "P7", "P5", "P3", "P1", "PZ", "P2", "PPO9H", "PPO5H", "PPO1", "PPO2", "PO9", "PO7", "PO3", "POZ", "PO4", "POO9H", "POO3H", "POO4H", "O1", "O2", "OI1H", "OI2H", "I1", "IZ", "I2"
]

interestingElectrodes = [
    "AFF2", "F3", "F1", "F2", "FFC3H", "FFC1H", "FFC2H", "FFC4H", "FC3", "FC1", "FCZ", "FC2", "FCC3H", "FCC1H", "FCC2H", "C3", "C1", "CZ", "C2", "CCP3H", "CCP1H", "CCP2H", "CCP4H", "CP3", "CP1", "CPZ", "CP2", "CPP3H", "CPP1H", "CPP2H", "CPP4H", "P3", "P1", "PZ", "P7", "P2", "PPO1", "PPO2", "PO3", "POZ", "PO4", "POO3H", "POO4H", "O1", "O2", "OI1H", "OI2H", "I1", "IZ", "I2"
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

### Normalize virtual electrode distances
maxX = max([x.pos[0] for x in virtualElectrodes])
minX = min([x.pos[0] for x in virtualElectrodes])
maxY = max([x.pos[1] for x in virtualElectrodes])
minY = min([x.pos[1] for x in virtualElectrodes])
for electrode in virtualElectrodes:
    electrode.normalizedPos = ((electrode.pos[0] - minX) / (maxX - minX), (electrode.pos[1] - minY) / (maxY - minY))

### Normalize detected electrode distances
maxX = max([x.position[0] for x in detectedElectrodes])
minX = min([x.position[0] for x in detectedElectrodes])
maxY = max([x.position[1] for x in detectedElectrodes])
minY = min([x.position[1] for x in detectedElectrodes])
for electrode in detectedElectrodes:
    electrode.normalizedPos = ((electrode.position[0] - minX) / (maxX - minX), (electrode.position[1] - minY) / (maxY - minY))



#assignments: dict[int, int] = {25: 56}
assignments: dict[int, int] = {22: 36, 19: 46, 27: 47, 25: 56}
#assignments: dict[int, int] = {26: 56, 31: 47, 22: 46}
#assignments: dict[int, int] = {}
allPossibilities: dict[int, list[int]] = {}

def distance2d(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

# Initialize first set of possibilities
alreadyAssignedDefined = [assignments[x] for x in assignments]
for i, detectedElectrode in enumerate(detectedElectrodes):
    if i in assignments:
        allPossibilities[i] = [assignments[i]]
        continue

    possibleChoices = [i for i, x in enumerate(definedElectrodes) if i not in alreadyAssignedDefined]

    # Filter Choices for interesting Electrodes
    possibleChoices = [x for x in possibleChoices if definedElectrodes[x].name in interestingElectrodes]

    # Filter for Colors
    possibleChoices = [x for x in possibleChoices if definedElectrodes[x].color == detectedElectrode.detectedColor]

    #possibleChoices = [x for x in possibleChoices if abs(definedElectrodes[x].distToFace - detectedElectrode.distToFace) < 0.3]

    #possibleChoices = [x for x in possibleChoices if distance2d(getVirtualElectrodeByName(definedElectrodes[x].name).normalizedPos, detectedElectrode.normalizedPos) < 0.4]

    allPossibilities[i] = possibleChoices

def checkDoneAssignments():
    # Check done Assignments
    for i, detectedElectrode in enumerate(detectedElectrodes):
        # Only one possibility left
        if len(allPossibilities[i]) == 1:
            assignments[i] = allPossibilities[i][0]

            for j, _ in enumerate(detectedElectrodes):
                if i != j:
                    allPossibilities[j] = [x for x in allPossibilities[j] if x != assignments[i]]

printState(allPossibilities)

minAssignments = 12

startTime = time.time()
while True:
    # Check if all assignments are done
    if len(assignments) >= minAssignments:
        break

    for i, detectedElectrode in enumerate(detectedElectrodes):
        # Already Assigned
        if i in assignments:
            continue

        # No Possibilities left
        if len(allPossibilities[i]) == 0:
            continue

        # Filter for Sequences
        newPossibilities = []
        for possibility in allPossibilities[i]:
            possElec = definedElectrodes[possibility]

            # Check Sequence
            currentSequence = detectedElectrode.detectedSequence
            #levDist = circularLevenshtein(currentSequence, getDefinedSequence(possElec))
            levDist = amountDifference(currentSequence, getDefinedSequence(possElec))

            if levDist > 3:
                continue

            # Check assigned Neighbors
            canBeRegardingAssignedNeighbors = True
            for n in [x for x in detectedElectrode.neighborIndexes if x in assignments]:
                ass = definedElectrodes[assignments[n]]
                if possElec.name not in ass.neighbors:
                    canBeRegardingAssignedNeighbors = False

            if not canBeRegardingAssignedNeighbors:
                continue

            # Check neighbors
            canBeRegardingNeighbors = False
            for n in detectedElectrode.neighborIndexes:
                poss2 = [definedElectrodes[x] for x in allPossibilities[n]]
                for p2 in poss2:
                    if possElec.name in p2.neighbors:
                        canBeRegardingNeighbors = True
                        break

            if not canBeRegardingNeighbors:
                continue

            newPossibilities.append(possibility)

        allPossibilities[i] = newPossibilities

        checkDoneAssignments()





    # Check Groups
    foundGroups = set()
    for i, detectedElectrode in enumerate(detectedElectrodes):
        currentGroup = allPossibilities[i]
        groupLength = len(currentGroup)

        if groupLength <= 1:
            continue

        groupCount = 1
        for j, detectedElectrode2 in enumerate(detectedElectrodes):
            if i == j:
                continue

            if allPossibilities[j] == currentGroup:
                groupCount += 1

        if groupCount >= groupLength:
            foundGroups.add(tuple(currentGroup))

    for group in foundGroups:
        print("Found Group: ", group, " in ")
        for i, detectedElectrode in enumerate(detectedElectrodes):
            if allPossibilities[i] == list(group):
                print(i)

    for group in foundGroups:
        print("Found Group: ", group)
        for i, detectedElectrode in enumerate(detectedElectrodes):
            if allPossibilities[i] != list(group):
                print("Removing from ", i, allPossibilities[i], " : ", group)
                allPossibilities[i] = [x for x in allPossibilities[i] if x not in group]

    checkDoneAssignments()
    printState(allPossibilities)

endTime = time.time()

print("Time: ", endTime - startTime)
print(assignments)
finalAssignments = {}
for key in allPossibilities:
    if len(allPossibilities[key]) == 1:
        finalAssignments[key] = [allPossibilities[key][0]]
    else:
        finalAssignments[key] = []
printState(finalAssignments)
