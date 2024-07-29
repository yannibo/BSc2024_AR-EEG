import time
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import matplotlib.animation as animation
import numpy as np

from matplotlib.path import Path

#https://github.com/EgoMoose/Articles/blob/master/Rodrigues'%20rotation/Rodrigues'%20rotation.md
def rotateAroundAxis(point, axis, theta):
    norm = axis / np.linalg.norm(axis)
    cos, sin = math.cos(theta), math.sin(theta)

    return point * cos + (1 - cos) * np.dot(point, norm) * norm + np.cross(norm, point) * sin

def cartToSpherical(point):
    x, y, z = point

    p = math.sqrt(
        math.pow(x, 2) +
        math.pow(y, 2) +
        math.pow(z, 2)
    )

    theta = math.atan2( z, math.sqrt(x**2 + y**2) )
    phi = math.atan2( y, x )

    return (p, theta, phi)




### 1.292






file = open("CA-106.nlr-colors-clean-4col.elc", "r")
#file = open("CA-106.nlr-colors-clean-4col-lefthalf.elc", "r")
lines = file.readlines()

electrodePos = {}
electrodeColors = {}

for l in lines:
    electrode = l.split(":")[0].strip()
    color = l.split(":")[1].strip()
    positions = l.split(":")[2].strip().split("\t")
    positions = [float(x) for x in positions]
    electrodePos[electrode] = positions

    if color == "yellow":
        electrodeColors[electrode] = "Y"
    elif color == "green":
        electrodeColors[electrode] = "G"
    elif color == "white" or color == "gray":
        electrodeColors[electrode] = "P"
    else:
        electrodeColors[electrode] = "X"

print(electrodePos)


electrodePosSpherical = {}

for electrode in electrodePos:
    electrodePosSpherical[electrode] = cartToSpherical(electrodePos[electrode])


def calculateDistance(pos1, pos2):
    return math.sqrt(
        math.pow(pos1[0] - pos2[0], 2) +
        math.pow(pos1[1] - pos2[1], 2)
    )

def generateButtonClicked(event):
    output = open("outputBackTrackAlgo.txt", "w")

    faceElectrode = "FPZ"

    #includeElectrodes = ["FP1", "FPZ", "FP2", "AFP3H", "AFP4H", "AF7", "AF3", "AFZ", "AF4", "AFF5H", "AFF1", "AFF2", "AFF6H", "F7", "F5", "F1", "FZ", "F2", "F6", "F8", "FFT7H", "FFC5H", "FFC3H", "FFC1H", "FFC4H", "FFC6H", "FFT8H", "FT7", "FC5", "FC1", "FCZ", "FC2", "FC4", "FC6", "FT8", "FTT7H", "FCC5H", "FCC3H", "FCC1H", "FCC2H", "FCC4H", "C3", "C1", "CZ", "C2", "C4", "C6", "CCP5H", "CCP3H", "CCP1H", "CCP2H", "CCP4H", "TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "CP4", "CP6", "TPP9H", "CPP5H", "CPP3H", "CPP1H", "CPP2H", "CPP4H", "CPP6H", "TPP10H", "P7", "P5", "P3", "PZ", "P2", "P4", "P6", "P8", "PPO9H", "PPO5H", "PPO1", "PPO10H", "PO7", "PO3", "POZ", "PO4", "PO8", "PO10", "POO3H", "POO4H", "POO10H"]

    for focusElec in electrodePos:
        #if focusElec not in includeElectrodes:
        #    continue

        centerElecPos = electrodePos[focusElec]
        centerElecPosSpher = cartToSpherical(centerElecPos)

        axis = np.cross(centerElecPos, [0, 0, 1])
        axis = axis / np.linalg.norm(axis)

        rotationAngle = (math.pi / 2) - (centerElecPosSpher[1])

        # Select Electrodes which are inside of the Theta Range
        selectedElectrodes = []
        for otherElec in electrodePos:
            if otherElec == focusElec:
                continue

            posRotated = rotateAroundAxis(np.array(electrodePos[otherElec]), axis, rotationAngle)
            posSpher = cartToSpherical(posRotated)

            #if abs(posSpher[1] - centerElecPosSpher[1]) < thetaAngleThreshold:
            if abs(posSpher[1]) > thetaAngleThreshold:
                selectedElectrodes.append({"angle": posSpher[2], "electrode": otherElec})


        selectedElectrodes.sort(key=lambda x: x["angle"])
        selectedElectrodes.reverse()

        nearColors = []
        for e in selectedElectrodes:
            nearColors.append(electrodeColors[e["electrode"]])

        distanceToFace = calculateDistance(electrodePos[focusElec], electrodePos[faceElectrode])

        result = 'DefinedElectrode("' + focusElec + '", "' + electrodeColors[focusElec] + '", ' + str(distanceToFace) + ', ["'
        result += '", "'.join([f'{e["electrode"]}' for e in selectedElectrodes])
        result += '"]),'

        output.write(result + "\n")

thetaAngleThreshold = .3
phiAngleThreshold = .3

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

def onpick(event):
    print(event.ind)
    electrode = list(electrodePos.keys())[event.ind[0]]
    global focusedElectrodeName
    focusedElectrodeName = electrode

fig.canvas.mpl_connect('pick_event', onpick)

thetaAngleThreshSlider = Slider(
    ax=plt.axes([0.25, 0.01, 0.65, 0.03]),
    label='\Theta Angle Threshold',
    valmin=0.1,
    valmax=2,
    valinit=0.3,
)

generateButton = Button(
    ax=plt.axes([0.8, 0.9, 0.1, 0.05]),
    label='Generate'
)

def updateTheta(val):
    global thetaAngleThreshold
    thetaAngleThreshold = val

thetaAngleThreshSlider.on_changed(updateTheta)

generateButton.on_clicked(generateButtonClicked)


focusedElectrodeName = "C3"

def animate(i):

    centerElecPos = electrodePos[focusedElectrodeName]
    centerElecPosSpher = cartToSpherical(centerElecPos)

    axis = np.cross(centerElecPos, [0, 0, 1])
    axis = axis / np.linalg.norm(axis)

    rotationAngle = (math.pi / 2) - (centerElecPosSpher[1])

    # Select Electrodes which are inside of the Theta Range
    selectedElectrodes = []
    for electrode in electrodePos:
        if electrode == focusedElectrodeName:
            continue

        posRotated = rotateAroundAxis(np.array(electrodePos[electrode]), axis, rotationAngle)
        posSpher = cartToSpherical(posRotated)

        #if abs(posSpher[1] - centerElecPosSpher[1]) < thetaAngleThreshold:
        if abs(posSpher[1]) > thetaAngleThreshold:
            selectedElectrodes.append(electrode)


    # Display Electrodes
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
    ax.scatter(x, y, z, c=colors, picker=True)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    """
    focusedElectrodePos = electrodePos[focusedElectrodeName]
    axis = np.cross(focusedElectrodePos, [0, 0, 1])
    axis = axis / np.linalg.norm(axis)

    ax.plot([axis[0] * -100, axis[0] * 100], [axis[1] * -100, axis[1] * 100], zs=[axis[2] * -100, axis[2] * 100])

    rotationAngle = (math.pi / 2) - (electrodePosSpherical[focusedElectrodeName][1]) #(math.pi / 180) *
    rotatedPoints = {}
    for electrode in electrodePos:
        #rotatedPoints[electrode] = rotate_points_around_axis(np.array([electrodePos[electrode]]), axis, rotationAngle)[0]
        rotatedPoints[electrode] = rotateAroundAxis(np.array(electrodePos[electrode]), axis, rotationAngle)

    x2, y2, z2, colors2 = [], [], [], []
    for electrode in electrodePos:
        x2.append(rotatedPoints[electrode][0])
        y2.append(rotatedPoints[electrode][1])
        z2.append(rotatedPoints[electrode][2])
        if electrode == focusedElectrodeName:
            colors2.append("yellow")
        else:
            colors2.append("pink")


    ax.scatter(x2, y2, z2, c=colors2)
    """




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