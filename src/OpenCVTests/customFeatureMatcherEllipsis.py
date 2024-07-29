import cv2
import numpy as np
from sklearn.neighbors import NearestNeighbors
import math
import time
import Levenshtein as lev
import matplotlib.pyplot as plt

#from scipy.spatial import distance_matrix
#from matplotlib import pyplot as plt

"""
This is the latest version of the detection amethod of electrodes from a camera image.
"""

# Some variables that can be adjusted using the UI of OpenCV when running this script
minArea = 200
ellipseRatioThreshold = 2.4
thresh = 100
maxArea = 3600
erodeDivider = 150 #200
inclusionCircle = 60 #70
levensteinThreshold = 1
colorYGThresh = 65
matchThreshold = 2.0
matchNumNeighbors = 3

def changeMinArea(val):
    global minArea
    minArea = val

def changeEllipseRatioThreshold(val):
    global ellipseRatioThreshold
    ellipseRatioThreshold = val / 10

def changeThreshold(val):
    global thresh
    thresh = val

def changeMaxArea(val):
    global maxArea
    maxArea = val

def changeErodeDivider(val):
    global erodeDivider
    erodeDivider = val

def changeInclusionCircle(val):
    global inclusionCircle
    inclusionCircle = val

def changeLevensteinThreshold(val):
    global levensteinThreshold
    levensteinThreshold = val

def changeColorYGThresh(val):
    global colorYGThresh
    colorYGThresh = val

def changeMatchThreshold(val):
    global matchThreshold
    matchThreshold = val / 10

def changeMatchNumNeighbors(val):
    global matchNumNeighbors
    matchNumNeighbors = val


source_window = 'Source'
cv2.namedWindow(source_window)
# create trackbars
cv2.createTrackbar('minArea:', source_window, minArea, 10000, changeMinArea)
cv2.createTrackbar('ellipseRatioThreshold:', source_window, int(ellipseRatioThreshold * 10), 100, changeEllipseRatioThreshold)

cv2.createTrackbar('threshold:', source_window, thresh, 1000, changeThreshold)
cv2.createTrackbar('maxArea:', source_window, maxArea, 10000, changeMaxArea)
cv2.createTrackbar('erodeDivider:', source_window, erodeDivider, 1000, changeErodeDivider)
cv2.createTrackbar('inclusionCircle:', source_window, inclusionCircle, 200, changeInclusionCircle)
cv2.createTrackbar('levensteinThreshold:', source_window, levensteinThreshold, 100, changeLevensteinThreshold)
cv2.createTrackbar('colorYGThresh:', source_window, colorYGThresh, 360, changeColorYGThresh)
#cv2.createTrackbar('matchThreshold:', source_window, int(matchThreshold * 10), 100, changeMatchThreshold)
#cv2.createTrackbar('matchNumNeighbors:', source_window, matchNumNeighbors, 10, changeMatchNumNeighbors)


## Open a camera stream or a video file
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("H:/Unity/Hololens Recordings/CapEllipseTesting/20240611_061811_HoloLens.mp4")
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, img = cap.read()

    ## if frame is read correctly ret is True
    #if not ret:
    #    print("Can't receive frame (stream end?). Exiting ...")
    #    break

    ## Or instead of Videos, this can also take images
    #img = cv2.imread("H:/Unity/BThesisSandbox/3D Model Cap/V2/20240312_155523.jpg")
    #img = cv2.imread("H:/Unity/Hololens Recordings/CapEllipseTesting/20240611_062154_HoloLens_cut.jpg")

    ## Adjust the size of the image to reduce processing needs and so that the visualizations fit on the screen
    height = img.shape[0]
    width = img.shape[1]

    maxsize = 2000

    if height > width:
        if height > maxsize:
            img = cv2.resize(img, (int(width * maxsize / height), maxsize))
    else:
        if width > maxsize:
            img = cv2.resize(img, (maxsize, int(height * maxsize / width)))



    ## converting image into grayscale image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #cv2.imshow('gray', gray)

    ## convert image into a HSV version for color detection later
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    ## Blur the image
    blur = cv2.medianBlur(gray, 11)
    #cv2.imshow('blur', blur)

    ## Apply the threshold to the blurred image. Threshold value can be modified in the UI
    _, threshold = cv2.threshold(blur, thresh, 255, cv2.THRESH_BINARY)
    #cv2.imshow('threshold', threshold)

    ## Remove small noise by using an "opening" operation of OpenCV
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=3)
    #cv2.imshow('opening', opening)

    ## Dilate the image to counter the shrinking by the opening operation
    dilate = cv2.dilate(opening, None, iterations=2)
    cv2.imshow('dilate', dilate)

    ## This lets you save the images to disk by pressing 's'
    if cv2.waitKey(1) == ord('s'):
        cv2.imwrite("original.jpg", img)
        cv2.imwrite("gray.jpg", gray)
        cv2.imwrite("blur.jpg", blur)
        cv2.imwrite("threshold.jpg", threshold)
        cv2.imwrite("opening.jpg", opening)
        cv2.imwrite("dilate.jpg", dilate)

    ## This class is used to store the information of each detected electrode
    class ElectrodeContour:
        def __init__(self, ellipse, contour, centerPos, color, colorStr):
            self.ellipse = ellipse
            self.contour = contour
            self.centerPos = centerPos
            self.color = color
            self.colorStr = colorStr
            self.hemispherePos = None

    ## Apply the Canny edge detection to the dilated image and the contour detection to the edges
    canny_output = cv2.Canny(dilate, 100, 100 * 2)
    contours, _ = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    ## Find the rotated rectangles and ellipses for each contour
    minEllipse = [None]*len(contours)
    for i, c in enumerate(contours):
        if c.shape[0] > 5:
            minEllipse[i] = cv2.fitEllipse(c)

    ## Initiate the total mask used for debugging the color masks of the electrodes in the color detection step
    totalMask = np.zeros(img.shape, img.dtype)

    ## Method used to calculate the distance between two points
    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    ## Filter Contours
    electrodes: list[ElectrodeContour] = []
    for i, c in enumerate(contours):
        ## Filter by min and max area
        area = cv2.contourArea(c)
        if area < minArea or area > maxArea:
            continue

        ## Filter by number of points in the detected shape
        if c.shape[0] <= 5:
            continue

        ## Filter by ellipse's moment of inertia
        sizeRatio = minEllipse[i][1][0] / minEllipse[i][1][1]
        if sizeRatio < (1 / ellipseRatioThreshold) or sizeRatio > ellipseRatioThreshold:
            continue

        ## Filter out duplicates
        nearFound = False
        for e in electrodes:
            if distance(e.centerPos, minEllipse[i][0]) < 20:
                nearFound = True
                break

        if not nearFound:
            centerPos = (int(minEllipse[i][0][0]), int(minEllipse[i][0][1]))
            electrodes.append(ElectrodeContour(minEllipse[i], c, centerPos, (0, 255, 255), "X"))


    ## Calculate Colors for each electrode
    for i, e in enumerate(electrodes):
        area = cv2.contourArea(e.contour)

        ## create mask for color detection by drawing the filled contour of each detected ellipse onto a black image
        mask = np.zeros(dilate.shape, np.uint8)
        cv2.drawContours(mask, [e.contour], -1, 255, cv2.FILLED)

        radius = max(e.ellipse[1]) / 2

        ## Erode the mask to remove a bit of the outer edge of the mask
        element = cv2.getStructuringElement(cv2.MORPH_ERODE, (int(radius / 10) + 1, int(radius / 10) + 1), (int(radius / 10), int(radius / 10)))
        mask = cv2.erode(mask, element)

        ## Erode the mask to remove the core of the electrode, which is always gray
        element2 = cv2.getStructuringElement(cv2.MORPH_ERODE, (2 * int(area/erodeDivider) + 1, 2 * int(area/erodeDivider) + 1), (int(area/erodeDivider), int(area/erodeDivider)))
        maskSmall = cv2.erode(mask, element2)
        mask = cv2.bitwise_xor(mask, maskSmall)

        ## Add this mask to the total mask image
        totalMask = cv2.bitwise_or(totalMask, cv2.bitwise_and(img, img, mask=mask))

        ## Calculate the mean color of the electrode using the mask
        mean = cv2.mean(hsv, mask)
        hue = mean[0] * 2

        ## Determine the color of the electrode based on the hue value and some color thresholds
        colStr = ""
        if hue > 0 and hue < colorYGThresh:
            colStr = "Y"
        elif hue > colorYGThresh and hue < 150:
            colStr = "G"
        elif hue > 240 and hue < 330:
            colStr = "P"
        else:
            colStr = "X"

        electrodes[i].colorStr = colStr

        #colStr += ": " + str(int(hue))

        ## calculate the RGB color value for the electrode
        colImg = np.uint8([[[mean[0], 255, 255]]])
        colBGR = cv2.cvtColor(colImg, cv2.COLOR_HSV2BGR)

        color = (int(colBGR[0][0][0]), int(colBGR[0][0][1]), int(colBGR[0][0][2]), 0.0)
        electrodes[i].color = color

        ## Draw the electrode as an ellipse
        cv2.ellipse(img, e.ellipse, color, 2)

        ## Draw text containing the color of the electrode near it
        #cv2.putText(img, colStr, e.centerPos, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

        ## Draw index of electrode
        #cv2.putText(img, str(i), e.centerPos, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)


    ## Method used to identify if a point is inside of an ellipse. It does not work. Don't ask why
    def pointInEllipse(point, ellipse):
        global img

        # h and k are x and y of the ellipse center
        h, k = ellipse[0]

        # a and b are the ellipse width and height (bounding box), which in combination of theta is the actual bounding box
        a, b = ellipse[1]
        theta = math.radians(ellipse[2])

        # Coordinates of the point to test
        x, y = point

        # Divide dimensions by 2 to get the "radius"
        a, b = a / 2, b / 2

        cos = math.cos(-theta)
        sin = math.sin(-theta)

        # Move Point to Origin, so that we can ignore the center of the ellipse and can rotate the point according to theta correctly
        x = x - h
        y = y - k

        # Rotate Point around origin by -theta
        x = x * cos - y * sin
        y = x * sin + y * cos

        #return (((x - h) * cos + (y - k) * sin) ** 2) / (a**2) + (((x - h) * sin - (y - k) * cos) ** 2) / (b**2) <= 1
        #return ((x - h) ** 2) / (a**2) + ((y - k) ** 2) / (b**2) <= 1

        # Check whether the point is inside the ellipse
        return (x ** 2) / (a ** 2) + (y ** 2) / (b ** 2) <= 1



    ## Method used to project electrode position onto a hemisphere
    def calculateHemispherePoints(electrodes, radius=4):
        points = np.array([(e.centerPos[0], -e.centerPos[1]) for e in electrodes])

        for i, e in enumerate(electrodes):
            (x, y) = e.centerPos
            y = -y
            # Normalize x, y to be in range [-1, 1]
            nx = (x - np.mean(points[:, 0])) / np.std(points[:, 0])
            ny = (y - np.mean(points[:, 1])) / np.std(points[:, 1])

            # Calculate the z-coordinate on the hemisphere
            nz = math.sqrt(max(0, radius**2 - nx**2 - ny**2))
            electrodes[i].hemispherePos = (nx, ny, nz)

    ## Calculate the hemisphere positions for all electrodes
    calculateHemispherePoints(electrodes)

    ## Data type used to feed detected electrodes into the iterative algorithm appended to this file
    class DetectedElectrodeAlgo:
        def __init__(self, detectedColor, detectedSequence, distToFace, neighborIndexes, position):
            self.detectedColor = detectedColor
            self.detectedSequence = detectedSequence
            self.distToFace = distToFace
            self.neighborIndexes = neighborIndexes
            self.position = position

    detectedElectrodes = []
    output = ""
    algoElectrodes = []
    czIndex = -1

    ## Determine neighbors and color sequence for all electrodes
    #for i, e in enumerate([electrodes[int(len(electrodes) / 2)]]):
    for i, e in enumerate(electrodes):
    #with electrodes[int(len(electrodes) / 2)] as e:
        #area = cv2.contourArea(e.contour)
        #inclusionRadius = inclusionCircle * (area / 1000)

        ## Calculating the inclusion radius based on the perimeter of the ellipse
        perimater = cv2.arcLength(e.contour, True)
        inclusionRadius = inclusionCircle * (perimater / 100)

        ## Draw the inclusion circle for one specific electrode
        if i == 37:
            cv2.circle(img, e.centerPos, int(inclusionRadius), e.color, 3)

        a, b = e.ellipse[1]
        if a < b:
            a = a * ((inclusionCircle + 100) / 40)
            b = b * ((inclusionCircle + 100) / 30)
        else:
            b = b * ((inclusionCircle + 100) / 40)
            a = a * ((inclusionCircle + 100) / 30)

        ## Calculate the bigger ellipse as the inclusion circle
        biggerEllipse = (e.ellipse[0], (a, b), e.ellipse[2])



        #if i == 27:
        #    cv2.ellipse(img, biggerEllipse, e.color, 1)

        ## Draw 100 points at random locations to test the pointInEllipse method
        """ for i in range(1000):
            x = np.random.randint(0, img.shape[1])
            y = np.random.randint(0, img.shape[0])
            if pointInEllipse((x, y), biggerEllipse):
                cv2.circle(img, (x, y), 5, (255, 255, 255), 5)
            else:
                cv2.circle(img, (x, y), 5, (0, 0, 0), 5) """

        foundElectrodes = []
        for i2, e2 in enumerate(electrodes):
            #if distance(e.centerPos, e2.centerPos) < inclusionRadius and e != e2:
            #if pointInEllipse(e2.centerPos, biggerEllipse) and e != e2:

            ## Determine neighbors based on their hemisphere position and distance
            hemiDistance = np.linalg.norm(np.array(e.hemispherePos) - np.array(e2.hemispherePos))
            if hemiDistance < (inclusionCircle / 40) and e != e2:
                if i == 37:
                    cv2.line(img, e.centerPos, e2.centerPos, e2.color, 2)

                angle = math.atan2(e2.centerPos[1] - e.centerPos[1], e2.centerPos[0] - e.centerPos[0])
                foundElectrodes.append({"color": e2.colorStr, "distance": distance(e.centerPos, e2.centerPos), "angle": angle, "index": i2})

        ## Costruct the color sequence based on the neighbors
        testColorSequence = ""

        foundElectrodes.sort(key=lambda x: x["angle"])
        for e2 in foundElectrodes:
            testColorSequence += e2["color"]

        #cv2.putText(img, testColorSequence, e.centerPos, cv2.FONT_HERSHEY_SIMPLEX, 1, e.color, 2, cv2.LINE_AA)

        ## Calculate the distance to "the face" (a point on the left of the screen)
        facePos = (0, int(img.shape[0] / 2))
        cv2.circle(img, facePos, 5, (255, 255, 255), 5)
        distToFace = distance(e.centerPos, facePos)

        ## Add detected electrode to debug output used for other files and the list of detected electrodes for the iterative algorithm at the bottom of this file
        output += f"DetectedElectrode(\"{e.colorStr}\", \"{testColorSequence}\", " + str(distToFace) + ", [" + ', '.join([str(x["index"]) for x in foundElectrodes]) + "], (" + str(e.centerPos[0]) + ", " + str(-e.centerPos[1]) + "), -1),\n"
        algoElectrodes.append(DetectedElectrodeAlgo(e.colorStr, testColorSequence, distToFace, [x["index"] for x in foundElectrodes], (e.centerPos[0], -e.centerPos[1])))

        ## Class used to contain information of the pre-defined reference electrodes
        class Electrode:
            def __init__(self, name, color, sequence):
                self.name = name
                self.color = color
                self.sequence = sequence

            def checkSequence(self, color, testSequence):
                testStr = self.sequence + self.sequence
                return testSequence in testStr # and color == self.color
                #return (lev.distance(testStr, testSequence) / len(testSequence) < levensteinThreshold) and color == self.color

                #levensteinDistance = 0
                #for i in range(len(testSequence)):
                #    if testSequence[i] != self.sequence[i]:
                #        levensteinDistance += 1
                #
                #return levensteinDistance / len(self.sequence) < levensteinThreshold and color == self.color


        ## List of pre-defined electrodes
        eDefs = [
            Electrode("C1", "G", "PYPYPXPX"),
            Electrode("CZ", "P", "GYGYGYGY"),
            Electrode("CP1", "P", "GYGYGXGX"),
            Electrode("FFC1H", "Y", "YGYPXGXP"),
            Electrode("AFZ", "X", "PXYYX"),
            Electrode("F2", "G", "PXPGXPY"),
        ]

        ## Method that concatenates a reference color string to itself and calls the levenshtein distance for each possible rotation of the string. Returns the minimum distance
        def circularLevenshtein(a, b):
            minDistance = float("inf")
            concatenated = a + a

            for i in range(len(a)):
                rotated = concatenated[i:i + len(a)]
                distance = lev.distance(rotated, b)
                if distance < minDistance:
                    minDistance = distance

            return minDistance

        ## Method that checks a test color string against all reference electrodes of the same color and returns the best match
        def checkTestColorSequence(eColor, testColorSequence, eDefs):
            distances = []
            for electrode in eDefs:
                if eColor != electrode.color:
                    continue

                dist = circularLevenshtein(electrode.sequence, testColorSequence)
                distances.append({"name": electrode.name, "distance": dist, "sequence": electrode.sequence, "eDef": electrode})

            distances.sort(key=lambda x: x["distance"])
            return distances[0] if len(distances) > 0 else None

        ## Check the test color sequence against all reference electrodes and store the best match
        bestEDef = checkTestColorSequence(e.colorStr, testColorSequence, eDefs)
        if bestEDef != None and len(testColorSequence) > 0 and bestEDef["distance"] <= levensteinThreshold:
            print(f"Electrode {bestEDef['name']} has the sequence {testColorSequence} with distance {bestEDef['distance']} to {bestEDef['sequence']}")
            #cv2.putText(img, e.colorStr + ": " + bestEDef["name"], e.centerPos, cv2.FONT_HERSHEY_SIMPLEX, 1, e.color, 2, cv2.LINE_AA)
            detectedElectrodes.append({
                "name": bestEDef["name"],
                "edef": bestEDef["eDef"],
                "contour": e
            })

            if bestEDef["name"] == "CZ":
                czIndex = i

        #strDistances = []
        #for electrode in eDefs:
            #if electrode.color != e.colorStr:
            #    continue

            #dist = lev.distance(electrode.sequence, testColorSequence)
            #strDistances.append({"name": electrode.name, "distance": dist})


            #if electrode.checkSequence(e.colorStr, testColorSequence) and len(testColorSequence) > 0.7 * len(electrode.sequence):
            #    print(f"Electrode {electrode.name} has the sequence {testColorSequence}")
            #    detectedElectrodes.append({
            #        "name": electrode.name,
            #        "edef": electrode,
            #        "contour": e
            #    })
            #    cv2.putText(img, electrode.name, e.centerPos, cv2.FONT_HERSHEY_SIMPLEX, 1, e.color, 2, cv2.LINE_AA)

        #strDistances.sort(key=lambda x: x["distance"])
        #bestMatch = strDistances[0]
        #if bestMatch["distance"] / len(testColorSequence) < levensteinThreshold:
            #print(f"Electrode {bestMatch['name']} has the sequence {testColorSequence} with distance {bestMatch['distance']}")
            #cv2.putText(img, bestMatch["name"], e.centerPos, cv2.FONT_HERSHEY_SIMPLEX, 1, e.color, 2, cv2.LINE_AA)

    ## Print the Debug output
    #print(output)


    ## This is the iterative algorithm copied into this file for testing.
    def doTheAlgo(detElectrodes, czIndex):
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

        class VirtualElectrode:
            def __init__(self, name, pos):
                self.name = name
                self.pos = pos
                self.normalizedPos = None

        virtualElectrodes = [
            VirtualElectrode("FP1", (402.6541,-597.4014)),
            VirtualElectrode("FPZ", (432.8985,-611.7068)),
            VirtualElectrode("FP2", (478.057,-624.0025)),
            VirtualElectrode("AFP3H", (415.1975,-617.4288)),
            VirtualElectrode("AFP4H", (455.0383,-633.4995)),
            VirtualElectrode("AF7", (370.293,-554.6786)),
            VirtualElectrode("AF3", (389.7059,-600.8289)),
            VirtualElectrode("AFZ", (436.4302,-633.1786)),
            VirtualElectrode("AF4", (493.6767,-638.2439)),
            VirtualElectrode("AF8", (517.0358,-613.2484)),
            VirtualElectrode("AFF5H", (375.4138,-572.4997)),
            VirtualElectrode("AFF1", (420.3699,-621.7473)),
            VirtualElectrode("AFF2", (465.3683,-640.1082)),
            VirtualElectrode("AFF6H", (529.7485,-626.0359)),
            VirtualElectrode("F7", (368.9369,-521.8837)),
            VirtualElectrode("F5", (368.8828,-547.7532)),
            VirtualElectrode("F3", (385.9018,-579.3515)),
            VirtualElectrode("F1", (414.3535,-608.5927)),
            VirtualElectrode("FZ", (449.9595,-630.7144)),
            VirtualElectrode("F2", (492.196,-639.5203)),
            VirtualElectrode("F4", (520.8162,-634.0114)),
            VirtualElectrode("F6", (545.4277,-616.9345)),
            VirtualElectrode("F8", (549.2852,-592.5278)),
            VirtualElectrode("FFT7H", (368.4104,-518.6694)),
            VirtualElectrode("FFC5H", (374.8656,-547.2763)),
            VirtualElectrode("FFC3H", (401.8601,-580.1962)),
            VirtualElectrode("FFC1H", (439.374,-612.3513)),
            VirtualElectrode("FFC2H", (478.9095,-630.4187)),
            VirtualElectrode("FFC4H", (525.0071,-630.109)),
            VirtualElectrode("FFC6H", (548.4636,-619.5354)),
            VirtualElectrode("FFT8H", (562.6917,-585.8611)),
            VirtualElectrode("FT9", (383.5425,-467.8602)),
            VirtualElectrode("FT7", (378.7448,-478.756)),
            VirtualElectrode("FC5", (372.1581,-505.9475)),
            VirtualElectrode("FC3", (393.4068,-546.5949)),
            VirtualElectrode("FC1", (428.893,-583.1755)),
            VirtualElectrode("FCZ", (471.9401,-613.006)),
            VirtualElectrode("FC2", (517.7527,-621.5073)),
            VirtualElectrode("FC4", (553.199,-617.7875)),
            VirtualElectrode("FC6", (572.4822,-593.5732)),
            VirtualElectrode("FT8", (566.9979,-561.5023)),
            VirtualElectrode("FTT9H", (388.0587,-459.0742)),
            VirtualElectrode("FTT7H", (381.2998,-472.9985)),
            VirtualElectrode("FCC5H", (385.6809,-503.8747)),
            VirtualElectrode("FCC3H", (418.6418,-543.6307)),
            VirtualElectrode("FCC1H", (465.0833,-577.7203)),
            VirtualElectrode("FCC2H", (511.3071,-604.6938)),
            VirtualElectrode("FCC4H", (557.2885,-604.5653)),
            VirtualElectrode("FCC6H", (584.8121,-592.7842)),
            VirtualElectrode("FTT8H", (586.4865,-562.5822)),
            VirtualElectrode("FTT10H", (576.212,-540.6422)),
            VirtualElectrode("T7", (394.3902,-443.6086)),
            VirtualElectrode("C5", (389.3801,-464.8005)),
            VirtualElectrode("C3", (409.9579,-504.145)),
            VirtualElectrode("C1", (454.9112,-540.7104)),
            VirtualElectrode("CZ", (500.1287,-572.8939)),
            VirtualElectrode("C2", (551.1663,-588.049)),
            VirtualElectrode("C4", (587.642,-583.2206)),
            VirtualElectrode("C6", (600.2536,-560.0982)),
            VirtualElectrode("T8", (591.1998,-530.5679)),
            VirtualElectrode("M1", (419.5243,-407.5476)),
            VirtualElectrode("TTP7H", (406.7057,-431.0422)),
            VirtualElectrode("CCP5H", (408.7232,-461.9747)),
            VirtualElectrode("CCP3H", (447.4009,-501.1945)),
            VirtualElectrode("CCP1H", (494.7079,-529.202)),
            VirtualElectrode("CCP2H", (540.3741,-555.1833)),
            VirtualElectrode("CCP4H", (583.7441,-563.2604)),
            VirtualElectrode("CCP6H", (609.5238,-554.0422)),
            VirtualElectrode("TTP8H", (603.9687,-527.9172)),
            VirtualElectrode("M2", (593.9519,-485.6071)),
            VirtualElectrode("TP7", (415.86,-413.9099)),
            VirtualElectrode("CP5", (417.5655,-425.631)),
            VirtualElectrode("CP3", (439.7451,-456.7714)),
            VirtualElectrode("CP1", (481.9052,-488.8363)),
            VirtualElectrode("CPZ", (530.3466,-515.7294)),
            VirtualElectrode("CP2", (579.279,-536.8733)),
            VirtualElectrode("CP4", (607.4847,-539.2728)),
            VirtualElectrode("CP6", (616.2781,-524.0244)),
            VirtualElectrode("TP8", (603.6201,-504.5787)),
            VirtualElectrode("TPP9H", (436.9196,-391.4738)),
            VirtualElectrode("TPP7H", (433.9203,-398.3017)),
            VirtualElectrode("CPP5H", (445.2849,-417.2841)),
            VirtualElectrode("CPP3H", (476.1573,-454.9526)),
            VirtualElectrode("CPP1H", (522.9396,-473.4899)),
            VirtualElectrode("CPP2H", (567.087,-495.1092)),
            VirtualElectrode("CPP4H", (603.2276,-512.5417)),
            VirtualElectrode("CPP6H", (622.0558,-505.4892)),
            VirtualElectrode("TPP8H", (614.6813,-494.2413)),
            VirtualElectrode("TPP10H", (608.1735,-471.4768)),
            VirtualElectrode("P9", (440.3276,-378.9927)),
            VirtualElectrode("P7", (446.9807,-386.5942)),
            VirtualElectrode("P5", (453.2159,-395.4483)),
            VirtualElectrode("P3", (472.5053,-414.026)),
            VirtualElectrode("P1", (508.3756,-436.3891)),
            VirtualElectrode("PZ", (552.4374,-458.6351)),
            VirtualElectrode("P2", (588.0401,-480.573)),
            VirtualElectrode("P4", (615.5261,-483.076)),
            VirtualElectrode("P6", (620.2042,-477.1132)),
            VirtualElectrode("P8", (611.5226,-466.345)),
            VirtualElectrode("P10", (610.2761,-447.866)),
            VirtualElectrode("PPO9H", (451.9804,-377.3774)),
            VirtualElectrode("PPO5H", (472.6106,-397.9748)),
            VirtualElectrode("PPO1", (534.9197,-427.3009)),
            VirtualElectrode("PPO2", (580.8237,-448.2159)),
            VirtualElectrode("PPO6H", (614.651,-460.9574)),
            VirtualElectrode("PPO10H", (606.3758,-446.7809)),
            VirtualElectrode("PO9", (486.2885,-363.4789)),
            VirtualElectrode("PO7", (483.7148,-371.6142)),
            VirtualElectrode("PO5", (487.4881,-375.241)),
            VirtualElectrode("PO3", (497.1635,-399.2185)),
            VirtualElectrode("POZ", (562.3467,-410.9075)),
            VirtualElectrode("PO4", (604.3118,-445.0058)),
            VirtualElectrode("PO6", (610.809,-442.4643)),
            VirtualElectrode("PO8", (608.0303,-435.9937)),
            VirtualElectrode("PO10", (602.8561,-423.1801)),
            VirtualElectrode("POO9H", (503.506,-368.9673)),
            VirtualElectrode("POO3H", (534.7441,-388.9072)),
            VirtualElectrode("POO4H", (578.3253,-407.2102)),
            VirtualElectrode("POO10H", (591.6398,-403.5875)),
            VirtualElectrode("O1", (517.9691,-373.3918)),
            VirtualElectrode("OZ", (555.8777,-384.883)),
            VirtualElectrode("O2", (585.7689,-404.9807)),
            VirtualElectrode("OI1H", (536.2555,-374.0852)),
            VirtualElectrode("OI2H", (569.5956,-387.0714)),
            VirtualElectrode("I1", (512.2266,-364.6174)),
            VirtualElectrode("IZ", (544.7339,-374.7458)),
            VirtualElectrode("I2", (584.625,-396.3521)),
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

        def distance2d(a, b):
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

        interestingElectrodes = [
            "AFF2", "F3", "F1", "F2", "FFC3H", "FFC1H", "FFC2H", "FFC4H", "FC3", "FC1", "FCZ", "FC2", "FCC3H", "FCC1H", "FCC2H", "C3", "C1", "CZ", "C2", "CCP3H", "CCP1H", "CCP2H", "CCP4H", "CP3", "CP1", "CPZ", "CP2", "CPP3H", "CPP1H", "CPP2H", "CPP4H", "P3", "P1", "PZ", "P7", "P2", "PPO1", "PPO2", "PO3", "POZ", "PO4", "POO3H", "POO4H", "O1", "O2", "OI1H", "OI2H", "I1", "IZ", "I2"
        ]


        ### Normalize DistanceToFace for defined Electrodes
        maxDist = max([x.distToFace for x in definedElectrodes])
        minDist = min([x.distToFace for x in definedElectrodes])
        for electrode in definedElectrodes:
            electrode.distToFace = (electrode.distToFace - minDist) / (maxDist - minDist)

        ### Normalize DistanceToFace for detected Electrodes
        maxDist = max([x.distToFace for x in detElectrodes])
        minDist = min([x.distToFace for x in detElectrodes])
        for electrode in detElectrodes:
            electrode.distToFace = (electrode.distToFace - minDist) / (maxDist - minDist)

        ### Normalize virtual electrode distances
        maxX = max([x.pos[0] for x in virtualElectrodes])
        minX = min([x.pos[0] for x in virtualElectrodes])
        maxY = max([x.pos[1] for x in virtualElectrodes])
        minY = min([x.pos[1] for x in virtualElectrodes])
        for electrode in virtualElectrodes:
            electrode.normalizedPos = ((electrode.pos[0] - minX) / (maxX - minX), (electrode.pos[1] - minY) / (maxY - minY))

        ### Normalize detected electrode distances
        maxX = max([x.position[0] for x in detElectrodes])
        minX = min([x.position[0] for x in detElectrodes])
        maxY = max([x.position[1] for x in detElectrodes])
        minY = min([x.position[1] for x in detElectrodes])
        for electrode in detElectrodes:
            electrode.normalizedPos = ((electrode.position[0] - minX) / (maxX - minX), (electrode.position[1] - minY) / (maxY - minY))




        assignments: dict[int, int] = {czIndex: 56}
        #assignments: dict[int, int] = {26: 56, 31: 47, 22: 46}
        #assignments: dict[int, int] = {}
        allPossibilities: dict[int, list[int]] = {}

        # Initialize first set of possibilities
        alreadyAssignedDefined = [assignments[x] for x in assignments]
        for i, detectedElectrode in enumerate(detElectrodes):
            if i in assignments:
                allPossibilities[i] = [assignments[i]]
                continue

            possibleChoices = [i for i, x in enumerate(definedElectrodes) if i not in alreadyAssignedDefined]

            # Filter Choices for interesting Electrodes
            possibleChoices = [x for x in possibleChoices if definedElectrodes[x].name in interestingElectrodes]

            # Filter for Colors
            possibleChoices = [x for x in possibleChoices if definedElectrodes[x].color == detectedElectrode.detectedColor]

            possibleChoices = [x for x in possibleChoices if abs(definedElectrodes[x].distToFace - detectedElectrode.distToFace) < 0.5]

            possibleChoices = [x for x in possibleChoices if distance2d(getVirtualElectrodeByName(definedElectrodes[x].name).normalizedPos, detectedElectrode.normalizedPos) < 0.4]

            allPossibilities[i] = possibleChoices

        def checkDoneAssignments():
            # Check done Assignments
            for i, detectedElectrode in enumerate(detElectrodes):
                # Only one possibility left
                if len(allPossibilities[i]) == 1:
                    assignments[i] = allPossibilities[i][0]

                    for j, _ in enumerate(detElectrodes):
                        if i != j:
                            allPossibilities[j] = [x for x in allPossibilities[j] if x != assignments[i]]


        minAssignments = 8

        startTime = time.time()
        counter = 0
        while counter < 20:
            counter += 1
            # Check if all assignments are done
            if len(assignments) >= minAssignments:
                break

            for i, detectedElectrode in enumerate(detElectrodes):
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
            for i, detectedElectrode in enumerate(detElectrodes):
                currentGroup = allPossibilities[i]
                groupLength = len(currentGroup)

                if groupLength <= 1:
                    continue

                groupCount = 1
                for j, detectedElectrode2 in enumerate(detElectrodes):
                    if i == j:
                        continue

                    if allPossibilities[j] == currentGroup:
                        groupCount += 1

                if groupCount >= groupLength:
                    foundGroups.add(tuple(currentGroup))

            for group in foundGroups:
                #print("Found Group: ", group, " in ")
                for i, detectedElectrode in enumerate(detElectrodes):
                    if allPossibilities[i] == list(group):
                        print(i)

            for group in foundGroups:
                #print("Found Group: ", group)
                for i, detectedElectrode in enumerate(detElectrodes):
                    if allPossibilities[i] != list(group):
                        #print("Removing from ", i, allPossibilities[i], " : ", group)
                        allPossibilities[i] = [x for x in allPossibilities[i] if x not in group]

            checkDoneAssignments()

        endTime = time.time()

        print("Time: ", endTime - startTime)
        print(assignments)
        finalAssignments = []
        for key in allPossibilities:
            if len(allPossibilities[key]) == 1:
                finalAssignments.append({
                    "name": definedElectrodes[allPossibilities[key][0]].name,
                    #"edef": bestEDef["eDef"],
                    "contour": electrodes[key]
                })
                cv2.putText(img, electrodes[key].colorStr + ": " + definedElectrodes[allPossibilities[key][0]].name, electrodes[key].centerPos, cv2.FONT_HERSHEY_SIMPLEX, 1, electrodes[key].color, 2, cv2.LINE_AA)

        return finalAssignments

    ## If there is en electrode that could be CZ based on its colors, predefine it for the iterative algorithm as a starting point
    if czIndex == -1:
        czMatches = [x for x in algoElectrodes if "X" not in x.detectedSequence and "P" not in x.detectedSequence and len(x.detectedSequence) > 4]
        if len(czMatches) == 1:
            czIndex = algoElectrodes.index(czMatches[0])

    ## Run the algorithm with the detected electrodes
    #if czIndex != -1:
    #    detectedElectrodes = doTheAlgo(algoElectrodes, czIndex)

    ## If enough electrode could be identified, run a PNP algorithm to try to get the 3D positions of them
    if len(detectedElectrodes) >= 4:
        file = open("CA-106.nlr-clean.elc", "r")
        lines = file.readlines()

        electrodePos = {}

        for l in lines:
            electrode = l.split(":")[0].strip()
            positions = l.split(":")[1].strip().split("\t")
            positions = [float(x) for x in positions]
            electrodePos[electrode] = (positions[0], positions[1], positions[2])

        objectPoints = []
        imagePoints = []
        for e in detectedElectrodes:
            objectPoints.append(electrodePos[e["name"]])
            imagePoints.append((e["contour"].centerPos[0], e["contour"].centerPos[1]))

        focalLength = img.shape[1]
        center = (img.shape[1] / 2, img.shape[0] / 2)
        cameraMatrix = np.array(
            [[focalLength, 0, center[0]],
            [0, focalLength, center[1]],
            [0, 0, 1]], dtype = "double"
        )

        distCoeffs = np.zeros((4,1)) # Assuming no lens distortion

        success, rvec, tvec, inliers = cv2.solvePnPRansac(
            np.array(objectPoints), # Coordinates of the 3D points
            np.array(imagePoints, dtype="double"), # Coordinates of the 2D points
            cameraMatrix, # Camera Matrix
            distCoeffs, # distCoeffs
            None, # rvec
            None, # tvec
            False, #useExtrinsicGuess
            100, #iterationsCount
            8, #reprojectionError
            0.8, #confidence
            None, #inliers
            cv2.SOLVEPNP_ITERATIVE #flags
        )

        print(f"Success: {success}")

        if success:
            #projected, jacobian = cv2.projectPoints(np.array(objectPoints), rvec, tvec, cameraMatrix, distCoeffs)
            projected, jacobian = cv2.projectPoints(np.array([electrodePos[x] for x in electrodePos]), rvec, tvec, cameraMatrix, distCoeffs)
            #for p in projected:
            #    cv2.circle(img, (int(p[0][0]), int(p[0][1])), 5, (255, 255, 255), 20)


    ## Draw the detected electrodes
    cv2.imshow('totalMask', totalMask)
    cv2.imshow('shapes', img)

    ## Show a matplotlib graph containing the hemisphere positions of the electrodes
    """
    if cv2.waitKey(1) == ord('g'):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        x = [e.hemispherePos[0] for i, e in enumerate(electrodes)]
        y = [e.hemispherePos[1] for i, e in enumerate(electrodes)]
        z = [e.hemispherePos[2] for i, e in enumerate(electrodes)]
        colors = []

        for i, electrode in enumerate(electrodes):
            color = "blue"
            if electrode.colorStr == "Y":
                color = "yellow"
            elif electrode.colorStr == "G":
                color = "green"
            elif electrode.colorStr == "P":
                color = "purple"

            colors.append(color)

        print(x)
        print(y)
        print(z)
        print(colors)


        ax.clear()
        ax.scatter(x, y, z, c=colors)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        plt.show()

    """

    ## Pause the loop and save the current frame
    if cv2.pollKey() == ord('p'):
        cv2.imwrite("paused.png", img)
        print("Waiting")
        time.sleep(0.3)
        while cv2.waitKey(0) != ord('r'):
            pass


    ## Display the resulting frame including the detected electrodes
    if cv2.waitKey(1) == ord('q'):
        break

    time.sleep(0.1)


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()