import cv2
import numpy as np
from sklearn.neighbors import NearestNeighbors
import math
import time
#from matplotlib import pyplot as plt

def euclidean_distance(point1, point2):
    """
    Euclidean distance between two points.
    :param point1: the first point as a tuple (a_1, a_2, ..., a_n)
    :param point2: the second point as a tuple (b_1, b_2, ..., b_n)
    :return: the Euclidean distance
    """
    a = np.array(point1)
    b = np.array(point2)

    return np.linalg.norm(a - b, ord=2)


def point_based_matching(point_pairs):
    """
    This function is based on the paper "Robot Pose Estimation in Unknown Environments by Matching 2D Range Scans"
    by F. Lu and E. Milios.

    :param point_pairs: the matched point pairs [((x1, y1), (x1', y1')), ..., ((xi, yi), (xi', yi')), ...]
    :return: the rotation angle and the 2D translation (x, y) to be applied for matching the given pairs of points
    """

    x_mean = 0
    y_mean = 0
    xp_mean = 0
    yp_mean = 0
    n = len(point_pairs)

    if n == 0:
        return None, None, None

    for pair in point_pairs:

        (x, y), (xp, yp) = pair

        x_mean += x
        y_mean += y
        xp_mean += xp
        yp_mean += yp

    x_mean /= n
    y_mean /= n
    xp_mean /= n
    yp_mean /= n

    s_x_xp = 0
    s_y_yp = 0
    s_x_yp = 0
    s_y_xp = 0
    for pair in point_pairs:

        (x, y), (xp, yp) = pair

        s_x_xp += (x - x_mean)*(xp - xp_mean)
        s_y_yp += (y - y_mean)*(yp - yp_mean)
        s_x_yp += (x - x_mean)*(yp - yp_mean)
        s_y_xp += (y - y_mean)*(xp - xp_mean)

    rot_angle = math.atan2(s_x_yp - s_y_xp, s_x_xp + s_y_yp)
    translation_x = xp_mean - (x_mean*math.cos(rot_angle) - y_mean*math.sin(rot_angle))
    translation_y = yp_mean - (x_mean*math.sin(rot_angle) + y_mean*math.cos(rot_angle))

    return rot_angle, translation_x, translation_y


def icp(reference_points, points, max_iterations=100, distance_threshold=0.3, convergence_translation_threshold=1e-3,
        convergence_rotation_threshold=1e-4, point_pairs_threshold=10, verbose=False):
    """
    An implementation of the Iterative Closest Point algorithm that matches a set of M 2D points to another set
    of N 2D (reference) points.

    :param reference_points: the reference point set as a numpy array (N x 2)
    :param points: the point that should be aligned to the reference_points set as a numpy array (M x 2)
    :param max_iterations: the maximum number of iteration to be executed
    :param distance_threshold: the distance threshold between two points in order to be considered as a pair
    :param convergence_translation_threshold: the threshold for the translation parameters (x and y) for the
                                              transformation to be considered converged
    :param convergence_rotation_threshold: the threshold for the rotation angle (in rad) for the transformation
                                               to be considered converged
    :param point_pairs_threshold: the minimum number of point pairs the should exist
    :param verbose: whether to print informative messages about the process (default: False)
    :return: the transformation history as a list of numpy arrays containing the rotation (R) and translation (T)
             transformation in each iteration in the format [R | T] and the aligned points as a numpy array M x 2
    """

    transformation_history = []

    nbrs = NearestNeighbors(n_neighbors=1, algorithm='kd_tree').fit(reference_points)

    for iter_num in range(max_iterations):
        if verbose:
            print('------ iteration', iter_num, '------')

        closest_point_pairs = []  # list of point correspondences for closest point rule

        distances, indices = nbrs.kneighbors(points)
        for nn_index in range(len(distances)):
            if distances[nn_index][0] < distance_threshold:
                closest_point_pairs.append((points[nn_index], reference_points[indices[nn_index][0]]))
            else:
                print('Point', points[nn_index], 'has distance', distances[nn_index][0], distance_threshold)

        # if only few point pairs, stop process
        if verbose:
            print('number of pairs found:', len(closest_point_pairs))
        if len(closest_point_pairs) < point_pairs_threshold:
            if verbose:
                print('No better solution can be found (very few point pairs)!')
            break

        # compute translation and rotation using point correspondences
        closest_rot_angle, closest_translation_x, closest_translation_y = point_based_matching(closest_point_pairs)
        if closest_rot_angle is not None:
            if verbose:
                print('Rotation:', math.degrees(closest_rot_angle), 'degrees')
                print('Translation:', closest_translation_x, closest_translation_y)
        if closest_rot_angle is None or closest_translation_x is None or closest_translation_y is None:
            if verbose:
                print('No better solution can be found!')
            break

        # transform 'points' (using the calculated rotation and translation)
        c, s = math.cos(closest_rot_angle), math.sin(closest_rot_angle)
        rot = np.array([[c, -s],
                        [s, c]])
        aligned_points = np.dot(points, rot.T)
        aligned_points[:, 0] += closest_translation_x
        aligned_points[:, 1] += closest_translation_y

        # update 'points' for the next iteration
        points = aligned_points

        # update transformation history
        transformation_history.append(np.hstack((rot, np.array([[closest_translation_x], [closest_translation_y]]))))

        # check convergence
        if (abs(closest_rot_angle) < convergence_rotation_threshold) \
                and (abs(closest_translation_x) < convergence_translation_threshold) \
                and (abs(closest_translation_y) < convergence_translation_threshold):
            if verbose:
                print('Converged!')
            break

    return transformation_history, points





cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, img = cap.read()

    #img = cv2.imread("H:/Unity/BThesisSandbox/3D Model Cap/V2/20240312_155418.jpg")

    # if frame is read correctly ret is True
    #if not ret:
    #    print("Can't receive frame (stream end?). Exiting ...")
    #    break
    # Our operations on the frame come here


    height = img.shape[0]
    width = img.shape[1]

    if height > width:
        if height > 1000:
            img = cv2.resize(img, (int(width * 1000 / height), 1000))
    else:
        if width > 1000:
            img = cv2.resize(img, (1000, int(height * 1000 / width)))


    # converting image into grayscale image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #cv2.imshow('gray', gray)

    blur = cv2.medianBlur(gray, 11)
    #cv2.imshow('blur', blur)

    _, threshold = cv2.threshold(blur, 140, 255, cv2.THRESH_BINARY)
    cv2.imshow('threshold', threshold)

    #Remove small noise
    #kernel = np.ones((2,2),np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=3)
    cv2.imshow('opening', opening)

    dilate = cv2.dilate(opening, None, iterations=2)
    cv2.imshow('dilate', dilate)

    class ElectrodeContour:
        def __init__(self, ellipse, contour, centerPos, color, colorStr):
            self.ellipse = ellipse
            self.contour = contour
            self.centerPos = centerPos
            self.color = color
            self.colorStr = colorStr
            self.hemispherePos = None

    canny_output = cv2.Canny(dilate, 100, 100 * 2)
    contours, _ = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find the rotated rectangles and ellipses for each contour
    minEllipse = [None]*len(contours)
    for i, c in enumerate(contours):
        if c.shape[0] > 5:
            minEllipse[i] = cv2.fitEllipse(c)

    totalMask = np.zeros(img.shape, img.dtype)

    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    # Filter Contours
    electrodes: list[ElectrodeContour] = []
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        if area < 200 or area > 3600:
            continue

        if c.shape[0] <= 5:
            continue

        sizeRatio = minEllipse[i][1][0] / minEllipse[i][1][1]
        if sizeRatio < (1 / 2.4) or sizeRatio > 2.4:
            continue

        nearFound = False
        for e in electrodes:
            if distance(e.centerPos, minEllipse[i][0]) < 20:
                nearFound = True
                break

        if not nearFound:
            centerPos = (int(minEllipse[i][0][0]), int(minEllipse[i][0][1]))
            electrodes.append(ElectrodeContour(minEllipse[i], c, centerPos, (0, 255, 255), "X"))


    for i, e in enumerate(electrodes):
        cv2.ellipse(img, e.ellipse, (255, 255, 255), 2)




    circlePoints = []
    for i, e in enumerate(electrodes):
        circlePoints.append([e.centerPos[0], e.centerPos[1]])

    #print(circlePoints)

    virtualPoints = []
    with open('virtualPoints.txt', 'r') as f:
        for line in f:
            #print(line[1:-2])
            #virtualPoints.append([float(x) for x in line[1:-2].split(",")[0:2]])
            virtualPoints.append([float(x.replace(",", ".")) for x in line.split("|")])

    #print(virtualPoints)
    print(img.shape)

    for i in virtualPoints:
        cv2.circle(img, (int(i[0]), int(i[1])), 2, (0, 0, 255), 5)

    circleDescriptors = np.array(circlePoints)
    virtualDescriptors = np.array(virtualPoints)

    desc1 = np.array(circleDescriptors, dtype=np.float32)
    desc2 = np.array(virtualDescriptors, dtype=np.float32)

    # create BFMatcher object
    #bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)

    # Match descriptors.
    #matches = bf.match(desc1, desc2)

    # Sort them in the order of their distance.
    #matches = sorted(matches, key=lambda x: x.distance)


    #print(virtualDescriptors)
    #print(circleDescriptors)

    if len(circleDescriptors) > 5:
        transform, newPoints = icp(circleDescriptors, virtualDescriptors, verbose=True, distance_threshold=10)
        #print(newPoints)
        for i in newPoints:
            cv2.circle(img, (int(i[0]), int(i[1])), 2, (255, 0, 0), 5)













    """ FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches2 = flann.knnMatch(desc1, desc2, k=2)


    # store all the good matches as per Lowe's ratio test.
    matches = []
    for m,n in matches2:
        if m.distance < 0.7*n.distance:
            matches.append(m)

    #matches = []
    #for m,n in matches2:
    #    matches.append(m)

    if len(matches) >= 10:
        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points1[i, :] = circleDescriptors[match.queryIdx]
            points2[i, :] = virtualDescriptors[match.trainIdx]

        # Find homography
        M, mask = cv2.findHomography(points1, points2, cv2.RANSAC, 5.0)

        # Assuming virtualDescriptors are the points you want to transform
        # Make sure points are reshaped correctly for cv2.perspectiveTransform
        points_transformed = cv2.perspectiveTransform(points1.reshape(1, -1, 2), M)

        # Draw circles at the transformed points locations on 'img'
        for i in points_transformed[0]:
            cv2.circle(img, (int(i[0]), int(i[1])), 5, (255, 255, 255), 5)  # Thickness of -1 fills the circle

    else:
        print( "Not enough matches are found - {}/{}".format(len(matches), 10) )
        matchesMask = None


    # Draw first 10 matches.
    for i in range(min(10, len(matches))):
        #print((circleDescriptors[matches[i].queryIdx][0], circleDescriptors[matches[i].queryIdx][1]))
        #print((virtualDescriptors[matches[i].trainIdx][0], virtualDescriptors[matches[i].trainIdx][1]))
        cv2.circle(img, (int(circleDescriptors[matches[i].queryIdx][0]), int(circleDescriptors[matches[i].queryIdx][1])), 5, (0, 255, 0), 2)
        cv2.circle(img, (int(virtualDescriptors[matches[i].trainIdx][0]), int(virtualDescriptors[matches[i].trainIdx][1])), 5, (0, 255, 0), 2)
        cv2.line(img, (int(circleDescriptors[matches[i].queryIdx][0]), int(circleDescriptors[matches[i].queryIdx][1])), (int(virtualDescriptors[matches[i].trainIdx][0]), int(virtualDescriptors[matches[i].trainIdx][1])), (0, 255, 0), 2) """





    # Display the resulting frame
    cv2.imshow('shapes', img)
    if cv2.waitKey(1) == ord('q'):
        break

    time.sleep(0.1)


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

