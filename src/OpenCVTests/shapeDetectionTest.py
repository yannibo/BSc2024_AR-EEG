import cv2
import numpy as np
#from matplotlib import pyplot as plt

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, img = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here

    # converting image into grayscale image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #cv2.imshow('gray', gray)

    blur = cv2.medianBlur(gray, 11)
    #cv2.imshow('blur', blur)

    _, threshold = cv2.threshold(blur, 140, 255, cv2.THRESH_BINARY)
    cv2.imshow('threshold', threshold)

    #Remove small noise
    #kernel = np.ones((2,2),np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=3)
    cv2.imshow('opening', opening)

    dilate = cv2.dilate(opening, None, iterations=2)
    cv2.imshow('dilate', dilate)


    """
    # setting threshold of gray image
    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # using a findContours() function
    contours, _ = cv2.findContours(
        threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    i = 0

    # list for storing names of shapes
    for contour in contours:

        # here we are ignoring first counter because
        # findcontour function detects whole image as shape
        if i == 0:
            i = 1
            continue

        x,y,w,h = cv2.boundingRect(contour)
        if w < 50 or h < 50:
            continue

        # cv2.approxPloyDP() function to approximate the shape
        approx = cv2.approxPolyDP(
            contour, 0.01 * cv2.arcLength(contour, True), True)

        # using drawContours() function
        cv2.drawContours(img, [contour], 0, (0, 0, 255), 5)

        # finding center point of shape
        M = cv2.moments(contour)
        if M['m00'] != 0.0:
            x = int(M['m10']/M['m00'])
            y = int(M['m01']/M['m00'])

        # putting shape name at center of each shape
        if len(approx) == 3:
            cv2.putText(img, 'Triangle', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        elif len(approx) == 4:
            cv2.putText(img, 'Quadrilateral', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        elif len(approx) == 5:
            cv2.putText(img, 'Pentagon', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        elif len(approx) == 6:
            cv2.putText(img, 'Hexagon', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        else:
            cv2.putText(img, 'circle', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    """
    rows = dilate.shape[0]
    circles = cv2.HoughCircles(dilate, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=50, param2=25, minRadius=1, maxRadius=100)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center
            cv2.circle(img, center, 1, (0, 100, 100), 3)
            # circle outline
            radius = i[2]
            cv2.circle(img, center, radius, (255, 0, 255), 3)



    # Find contours and filter using contour area and aspect ratio
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        area = cv2.contourArea(c)
        if len(approx) > 5 and area > 100 and area < 4000:
            ((x, y), r) = cv2.minEnclosingCircle(c)
            cv2.circle(img, (int(x), int(y)), int(r), (36, 255, 12), 2)

    ref = cv2.imread('ref.png', cv2.IMREAD_GRAYSCALE)
    #orb = cv2.ORB_create()

    #kp1, des1 = orb.detectAndCompute(gray,None)
    #kp2, des2 = orb.detectAndCompute(ref,None)

    ## create BFMatcher object
    #bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)


    # Match descriptors.
    #matches = bf.match(des1,des2)

    # Sort them in the order of their distance.
    #matches = sorted(matches, key = lambda x:x.distance)

    # Draw first 10 matches.
    #img3 = cv2.drawMatches(gray,kp1,ref,kp2,matches[:10],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)





    """
    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(ref,None)
    kp2, des2 = sift.detectAndCompute(gray,None)
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)

    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)

    if len(good)>10:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        matchesMask = mask.ravel().tolist()
        h,w = ref.shape
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        if M is not None:
            dst = cv2.perspectiveTransform(pts,M)
            gray = cv2.polylines(gray,[np.int32(dst)],True,255,3, cv2.LINE_AA)
    else:
        print( "Not enough matches are found - {}/{}".format(len(good), 10) )
        matchesMask = None

    draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                singlePointColor = None,
                matchesMask = matchesMask, # draw only inliers
                flags = 2)
    img3 = cv2.drawMatches(ref,kp1,gray,kp2,good,None,**draw_params)
    cv2.imshow('feature', img3)
    """

    # Display the resulting frame
    cv2.imshow('shapes', img)
    if cv2.waitKey(1) == ord('q'):
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

