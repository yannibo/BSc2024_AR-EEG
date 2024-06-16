import time
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import matplotlib.animation as animation

file = open("CA-106.nlr-clean.elc", "r")
lines = file.readlines()

electrodePos = {}

for l in lines:
    electrode = l.split(":")[0].strip()
    positions = l.split(":")[1].strip().split("\t")
    positions = [float(x) for x in positions]
    electrodePos[electrode] = positions

print(electrodePos)


electrodePosSpherical = {}

for electrode in electrodePos:
    x, y, z = electrodePos[electrode]

    p = math.sqrt(
        math.pow(x, 2) +
        math.pow(y, 2) +
        math.pow(z, 2)
    )

    theta = math.atan2( y, x )

    phi = math.acos(
        z / p
    )

    electrodePosSpherical[electrode] = (p, theta, phi)


thetaAngleThreshold = .3
phiAngleThreshold = .3
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

thetaAngleThreshSlider = Slider(
    ax=plt.axes([0.25, 0.01, 0.65, 0.03]),
    label='\Theta Angle Threshold',
    valmin=0.1,
    valmax=2,
    valinit=0.3,
)

phiAngleThreshSlider = Slider(
    ax=plt.axes([0.25, 0.05, 0.65, 0.03]),
    label='\Phi Angle Threshold',
    valmin=0.1,
    valmax=2,
    valinit=0.3,
)

def updateTheta(val):
    global thetaAngleThreshold
    thetaAngleThreshold = val

def updatePhi(val):
    global phiAngleThreshold
    phiAngleThreshold = val

thetaAngleThreshSlider.on_changed(updateTheta)
phiAngleThreshSlider.on_changed(updatePhi)

focusedElectrodeName = "C6"

def animate(i):

    startPos = electrodePosSpherical[focusedElectrodeName]
    selectedElectrodes = []

    for electrode in electrodePosSpherical:
        if electrode == focusedElectrodeName:
            continue

        pos = electrodePosSpherical[electrode]

        if abs(pos[1] - startPos[1]) < thetaAngleThreshold and abs(pos[2] - startPos[2]) < phiAngleThreshold:
            print(f"Electrode {electrode} is at the same angle as {focusedElectrodeName}")
            selectedElectrodes.append(electrode)

    x = [electrodePos[focusedElectrodeName][0]]
    y = [electrodePos[focusedElectrodeName][1]]
    z = [electrodePos[focusedElectrodeName][2]]
    colors = ["red"]

    for electrode in electrodePos:
        if electrode == focusedElectrodeName:
            continue

        x.append(electrodePos[electrode][0])
        y.append(electrodePos[electrode][1])
        z.append(electrodePos[electrode][2])
        if electrode in selectedElectrodes:
            colors.append("green")
        else:
            colors.append("blue")

    ax.clear()
    ax.scatter(x, y, z, c=colors)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')





ani = animation.FuncAnimation(fig, animate, interval=100)
plt.show()


"""

class Electrode:
    def __init__(self, name, color, sequence):
        self.name = name
        self.color = color
        self.sequence = sequence

    def checkSequence(self, testSequence):
        testStr = self.sequence + self.sequence
        return testSequence in testStr



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
"""