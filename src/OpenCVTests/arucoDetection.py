import cv2
import numpy as np

arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
arucoParams = cv2.aruco.DetectorParameters()

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, img = cap.read()

    height = img.shape[0]
    width = img.shape[1]

    if height > width:
        if height > 1000:
            img = cv2.resize(img, (int(width * 1000 / height), 1000))
    else:
        if width > 1000:
            img = cv2.resize(img, (1000, int(height * 1000 / width)))


    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, arucoDict, parameters=arucoParams)

    if ids is not None:
        # Draw detected markers

        focalLength = img.shape[1]
        center = (img.shape[1] / 2, img.shape[0] / 2)
        cameraMatrix = np.array(
            [[focalLength, 0, center[0]],
            [0, focalLength, center[1]],
            [0, 0, 1]], dtype = "double"
        )

        distCoeffs = np.zeros((4,1)) # Assuming no lens distortion

        markerLength = 0.01 # Marker length in meters

        objPoints = list(range(4))
        objPoints[0] = (-markerLength/2, markerLength/2, 0)
        objPoints[1] = (markerLength/2, markerLength/2, 0)
        objPoints[2] = (markerLength/2, -markerLength/2, 0)
        objPoints[3] = (-markerLength/2, -markerLength/2, 0)
        objPoints = np.array(objPoints)

        for i, markerID in enumerate(ids):
            success, rvec, tvec = cv2.solvePnP(objPoints, corners[i], cameraMatrix, distCoeffs)
            print(tvec)
            cv2.drawFrameAxes(img, cameraMatrix, distCoeffs, rvec, tvec, markerLength * 1.5, 2)




        cv2.aruco.drawDetectedMarkers(img, corners, ids)

        for i in range(len(ids)):
            c = corners[i][0]
            x = (c[0][0] + c[2][0]) / 2
            y = (c[0][1] + c[2][1]) / 2
            cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)


    cv2.imshow('frame', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break