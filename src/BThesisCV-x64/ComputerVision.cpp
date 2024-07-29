#include <opencv2/opencv.hpp>

using namespace cv;

struct Color32
{
	uchar red;
	uchar green;
	uchar blue;
	uchar alpha;
};

struct Vector3
{
	float x;
	float y;
	float z;
};

struct DetectedElectrode {
	RotatedRect ellipse;
	Point centerPos;
	std::vector<Point> contour;
	char colorStr;
	Scalar_<uint8_t> bgrColor;
	Vec3f hemispherePosition;
};

/*struct DetectedElectrodeData {
	Vec2i centerPos;
	char colorStr;
	float distanceToFace;
	std::vector<int>* neighborIndexes;
};*/

struct DetectedElectrodeData {
	Vec2i centerPos;
	char colorStr;
	float distanceToFace;
	std::vector<int> neighborIndexes;
};

struct DetectedArucoMarker {
	int id;
	Vec2i center;
	Vec2f size;
	Vec3f rvec;
	Vec3f tvec;
};

template struct std::vector<Vec3f>;

extern "C"
{

	float distance2d(Point a, Point b) {
		return sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2));
	}

	/*__declspec(dllexport) void ProcessImage(Color32** rawImage, int width, int height)
	{

		// create an opencv object sharing the same data space
		Mat image(height, width, CV_8UC4, *rawImage);

		// start with flip (in both directions) if your image looks inverted
		flip(image, image, -1);

		// start processing the image
		// ************************************************

		Mat edges;
		Canny(image, edges, 50, 200);
		dilate(edges, edges, (5, 5));
		cvtColor(edges, edges, COLOR_GRAY2RGBA);
		normalize(edges, edges, 0, 1, NORM_MINMAX);
		multiply(image, edges, image);

		// end processing the image
		// ************************************************

		// flip again (just vertically) to get the right orientation
		//flip(image, image, 0);
	}

	double distance3d(Vec3d a, Vec3d b) {
		return sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2) + pow(a[2] - b[2], 2));
	}

	bool angleSort(Vec3d a, Vec3d b) {
		return a[1] < b[1];
	}

	__declspec(dllexport) int FindElectrodes(Color32** rawImage, DetectedElectrodeData* detectedElectrodes, int maxElectrodes, int width, int height, int thresholdValue, int kernelSize, double minArea, double maxArea, float ellipseRatioThreshold, int erodeDivider, int colorYGThresh, int inclusionCircle, int facePosX, int facePosY)
	{

		// create an opencv object sharing the same data space
		Mat image(height, width, CV_8UC4, *rawImage);

		// start with flip (in both directions) if your image looks inverted
		flip(image, image, 0);

		// start processing the image
		// ************************************************
		Mat gray(height, width, CV_8UC1);
		cvtColor(image, gray, ColorConversionCodes::COLOR_BGR2GRAY);

		Mat hsv(height, width, CV_8UC4);
		cvtColor(image, hsv, ColorConversionCodes::COLOR_BGR2HSV);

		Mat blur(height, width, CV_8UC1);
		medianBlur(gray, blur, 11);

		Mat thresh(height, width, CV_8UC1);
		threshold(blur, thresh, thresholdValue, 255, ThresholdTypes::THRESH_BINARY);

		Mat kernel = getStructuringElement(MorphShapes::MORPH_ELLIPSE, Size(kernelSize, kernelSize));
		
		Mat opening(height, width, CV_8UC1);
		morphologyEx(thresh, opening, MorphTypes::MORPH_OPEN, kernel, Point(-1, -1), 3);

		Mat dila(height, width, CV_8UC1);
		dilate(opening, dila, NULL, Point(-1, -1), 2);
		//imshow("dila", dila);

		
		Mat cannyOutput(height, width, CV_8UC1);
		Canny(dila, cannyOutput, 100, 100 * 2);

		std::vector<std::vector<Point>> contours;
		std::vector<Vec4i> hierarchy;
		findContours(cannyOutput, contours, RetrievalModes::RETR_TREE, ContourApproximationModes::CHAIN_APPROX_SIMPLE);

		std::vector<DetectedElectrode> electrodes;

		// Filter Contours 
		for (size_t i = 0; i < contours.size(); i++) {
			double area = contourArea(contours[i]);

			if (contours[i].size() > 5 && area >= minArea && area <= maxArea) {
				RotatedRect minEllipse = fitEllipse(contours[i]);

				float sizeRatio = minEllipse.size.width / minEllipse.size.height;
				if (sizeRatio < (1 / ellipseRatioThreshold) || sizeRatio > ellipseRatioThreshold) {
					continue;
				}

				bool duplicateFound = false;
				for (int i = 0; i < electrodes.size(); i++) {
					if (distance2d(electrodes[i].centerPos, minEllipse.center) < 20) {
						duplicateFound = true;
						break;
					}
				}

				if (!duplicateFound) {
					DetectedElectrode elec;

					elec.contour = contours[i];
					elec.ellipse = minEllipse;
					elec.centerPos = minEllipse.center;

					electrodes.push_back(elec);
				}
			}
		}

		// Detect the Color of Contours
		for (int i = 0; i < electrodes.size(); i++) {
			double area = contourArea(electrodes[i].contour);

			Mat mask(dila.rows, dila.cols, dila.type());
			drawContours(mask, electrodes[i].contour, -1, 255, FILLED);

			float radius = max(electrodes[i].ellipse.size.width, electrodes[i].ellipse.size.height);

			Mat element1 = getStructuringElement(MORPH_ERODE, Size((int)(radius / 10) + 1, (int)(radius / 10) + 1));
			erode(mask, mask, element1);


			Mat element2 = getStructuringElement(MORPH_ERODE, Size(2 * (int)(area / erodeDivider) + 1, (2 * (int)(area / erodeDivider) + 1)));
			Mat maskSmall(dila.rows, dila.cols, dila.type());
			erode(mask, maskSmall, element2);

			bitwise_xor(mask, maskSmall, mask);

			Scalar meanColor = mean(hsv, mask);
			int meanHue = meanColor[0] * 2;

			if (meanHue > 0 && meanHue < colorYGThresh) electrodes[i].colorStr = 'Y';
			else if (meanHue > colorYGThresh && meanHue < 150) electrodes[i].colorStr = 'G';
			else if (meanHue > 240 && meanHue < 330) electrodes[i].colorStr = 'P';
			else electrodes[i].colorStr = 'X';

			Scalar_<uint8_t> newColor(meanColor[0], 255, 255);
			Mat colImg(1, 1, CV_8UC3, newColor);
			Mat colBGR(1, 1, CV_8UC3);
			cvtColor(colImg, colBGR, COLOR_HSV2BGR);
			Scalar_<uint8_t> bgrColor = colBGR.at<Scalar_<uint8_t>>(0, 0);

			electrodes[i].bgrColor = bgrColor;
		}

		// Calculate the Hemisphere positions

		float hemisphereRadius = 3.0;
		float meanX = 0;
		float meanY = 0;
		float varX = 0;
		float varY = 0;

		// Calculate Mean of X and Y coordinates
		for (int i = 0; i < electrodes.size(); i++) {
			meanX += electrodes[i].centerPos.x / electrodes.size();
			meanY += electrodes[i].centerPos.y / electrodes.size();
		}

		// Calculate Variance and Standard Deviation of X and Y coordinates
		for (int i = 0; i < electrodes.size(); i++) {
			varX += pow(electrodes[i].centerPos.x - meanX, 2);
			varY += pow(electrodes[i].centerPos.y - meanY, 2);
		}

		varX /= electrodes.size();
		varY /= electrodes.size();

		float sdX = sqrt(varX);
		float sdY = sqrt(varY);

		for (int i = 0; i < electrodes.size(); i++) {
			int x = electrodes[i].centerPos.x;
			int y = -electrodes[i].centerPos.y;

			double nx = (x - meanX) / sdX;
			double ny = (y - meanY) / sdY;

			double nz = sqrt(max((double)0, pow(hemisphereRadius, 2) - pow(nx, 2) - pow(ny, 2)));
			electrodes[i].hemispherePosition = Vec3d(nx, ny, nz);
		}

		std::vector<DetectedElectrodeData> electrodeData;

		for (int i = 0; i < electrodes.size(); i++) {

			std::vector<Vec3d> foundElectrodes;

			// Search for neighbors
			for (int o = 0; o < electrodes.size(); o++) {
				double hemiDistance = distance3d(electrodes[i].hemispherePosition, electrodes[o].hemispherePosition);
				if (i != o && hemiDistance < ((double)inclusionCircle / 40)) {
					double angle = atan2(electrodes[o].centerPos.y - electrodes[i].centerPos.y, electrodes[o].centerPos.x - electrodes[i].centerPos.x);
					foundElectrodes.push_back(Vec3d(o, angle));
				}
			}

			// Sort for angle
			std::sort(foundElectrodes.begin(), foundElectrodes.end(), angleSort);

			std::vector<int> neighborIndexes;
			for (int i = 0; i < foundElectrodes.size(); i++) {
				neighborIndexes.push_back(foundElectrodes[i][0]);
			}

			double distToFace = distance2d(electrodes[i].centerPos, Point(facePosX, facePosY));

			DetectedElectrodeData eData = DetectedElectrodeData();
			eData.centerPos = Vec2i(electrodes[i].centerPos.x, electrodes[i].centerPos.y);
			eData.colorStr = electrodes[i].colorStr;
			eData.distanceToFace = distToFace;
			eData.neighborIndexes = neighborIndexes;

			electrodeData.push_back(eData);
		}

		for (int i = 0; i < min(maxElectrodes, (int)electrodeData.size()); i++)
		{
			//returnArr[i] = electrodeData[i];
			detectedElectrodes[i].centerPos = electrodeData[i].centerPos;
			detectedElectrodes[i].colorStr = electrodeData[i].colorStr;
			detectedElectrodes[i].distanceToFace = electrodeData[i].distanceToFace;
			detectedElectrodes[i].neighborIndexes = electrodeData[i].neighborIndexes;
		}

		//detectedElectrodes = &returnArr[0];


		// end processing the image
		// ************************************************

		// flip again (just vertically) to get the right orientation
		//flip(image, image, 0);
		flip(image, image, 0);
		//return circles.;
		return electrodeData.size();
	}*/

	__declspec(dllexport) int FindMarkers(Color32** rawImage, DetectedArucoMarker* detectedMarkers, int maxMarkers, int width, int height, float markerLength) {
		// create an opencv object sharing the same data space
		Mat image(height, width, CV_8UC4, *rawImage);

		// start with flip (in both directions) if your image looks inverted
		flip(image, image, 0);

		// start processing the image
		// ************************************************

		aruco::Dictionary arucoDict = aruco::getPredefinedDictionary(aruco::DICT_4X4_50);
		aruco::DetectorParameters arucoParams = aruco::DetectorParameters();

		Mat gray(height, width, CV_8UC1);
		cvtColor(image, gray, ColorConversionCodes::COLOR_BGR2GRAY);

		aruco::ArucoDetector detector(arucoDict, arucoParams);

		std::vector<int> markerIds;
		std::vector<std::vector<cv::Point2f>> markerCorners;

		detector.detectMarkers(gray, markerCorners, markerIds);



		int focalLength = width;
		Vec2f center(width / 2.f, height / 2.f);

		Matx33f cameraMatrix(
			focalLength, 0, center[0],
			0, focalLength, center[1],
			0, 0, 1
		);
		
		cv::Mat objPoints(4, 1, CV_32FC3);
		objPoints.ptr<Vec3f>(0)[0] = Vec3f(-markerLength / 2.f, markerLength / 2.f, 0);
		objPoints.ptr<Vec3f>(0)[1] = Vec3f(markerLength / 2.f, markerLength / 2.f, 0);
		objPoints.ptr<Vec3f>(0)[2] = Vec3f(markerLength / 2.f, -markerLength / 2.f, 0);
		objPoints.ptr<Vec3f>(0)[3] = Vec3f(-markerLength / 2.f, -markerLength / 2.f, 0);

		for (int i = 0; i < min(maxMarkers, (int)markerIds.size()); i++)
		{
			Vec3f rvec, tvec;

			bool success = solvePnP(objPoints, markerCorners.at(i), cameraMatrix, Matx14f(0, 0, 0, 0), rvec, tvec);

			int midX = (markerCorners[i][0].x + markerCorners[i][0].x) / 2;
			int midY = (markerCorners[i][0].y + markerCorners[i][0].y) / 2;

			float width = distance2d(markerCorners[i][0], markerCorners[i][1]);
			float height = distance2d(markerCorners[i][1], markerCorners[i][2]);

			detectedMarkers[i].center = Vec2i(midX, midY);
			detectedMarkers[i].id = markerIds[i];
			detectedMarkers[i].size = Vec2f(width, height);
			detectedMarkers[i].rvec = rvec;
			detectedMarkers[i].tvec = tvec;
		}

		// end processing the image
		// ************************************************

		// flip again (just vertically) to get the right orientation
		//flip(image, image, 0);
		flip(image, image, 0);
		//return circles.;
		return markerIds.size();
	}
}