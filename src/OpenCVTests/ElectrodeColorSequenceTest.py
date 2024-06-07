class Electrode:
    def __init__(self, name, color, sequence):
        self.name = name
        self.color = color
        self.sequence = sequence

    def checkSequence(self, testSequence):
        testStr = self.sequence + self.sequence
        return testSequence in testStr

"""
FTT8h: (Y): XYGYXG
FT8: (G): YXXYXY
T8: (X): YGYGY
FTT10h: (Y): GXXY
TTP8h: (Y): GXGYX
C6: (G): XXYYXX
CP6: (X): XGYYGX
CCP6h: (X): XXGXXG
"""

electrodes = [
    Electrode("FTT8h", "Y", "XYGYXG"),
    Electrode("FT8", "G", "YXXYXY"),
    Electrode("T8", "X", "YGYGY"),
    Electrode("FTT10h", "Y", "GXXY"),
    Electrode("TTP8h", "Y", "GXGYX"),
    Electrode("C6", "G", "XXYYXX"),
    Electrode("CP6", "X", "XGYYGX"),
    Electrode("CCP6h", "X", "XXGXXG")
]

testSequence = "YYGXXG"

for electrode in electrodes:
    if electrode.checkSequence(testSequence):
        print(f"Electrode {electrode.name} has the sequence {testSequence}")
