#include "pch.h"
#include "BThesisCV.h"

#include <opencv2/opencv.hpp>

using namespace cv;

#define DLL_EXPORT __declspec(dllexport)

struct Color32
{
	uchar red;
	uchar green;
	uchar blue;
	uchar alpha;
};

struct DetectedArucoMarker {
	int id;
	Vec2i center;
	Vec2f size;
	Vec3f rvec;
	Vec3f tvec;
};

extern "C" {
    DLL_EXPORT int getSomeInt()
    {
        return 42;
    }

	float distance2d(Point a, Point b) {
		return sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2));
	}

	DLL_EXPORT int FindMarkers(Color32** rawImage, DetectedArucoMarker* detectedMarkers, int maxMarkers, int width, int height, float markerLength) {
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



		/*int focalLength = width;
		Vec2f center(width / 2.f, height / 2.f);

		Matx33f cameraMatrix(
			focalLength, 0, center[0],
			0, focalLength, center[1],
			0, 0, 1
		);*/

		Matx33f cameraMatrix(
			959.9846086664326, 0, 627.8583345408457,
			0, 959.7559746370807, 337.39083466687356,
			0, 0, 1
		);

		double distCoeffs[5] = { 
			0.001802776900431189,
			-0.06346753848021745,
			0.00021717810386753987,
			-0.0009146816299671877,
			0.0 };
		Mat DistortionCoef = Mat(1, 5, CV_64FC1, distCoeffs);

		cv::Mat objPoints(4, 1, CV_32FC3);
		objPoints.ptr<Vec3f>(0)[0] = Vec3f(-markerLength / 2.f, markerLength / 2.f, 0);
		objPoints.ptr<Vec3f>(0)[1] = Vec3f(markerLength / 2.f, markerLength / 2.f, 0);
		objPoints.ptr<Vec3f>(0)[2] = Vec3f(markerLength / 2.f, -markerLength / 2.f, 0);
		objPoints.ptr<Vec3f>(0)[3] = Vec3f(-markerLength / 2.f, -markerLength / 2.f, 0);

		for (int i = 0; i < min(maxMarkers, (int)markerIds.size()); i++)
		{
			Vec3f rvec, tvec;

			bool success = solvePnP(objPoints, markerCorners.at(i), cameraMatrix, DistortionCoef, rvec, tvec, false, cv::SOLVEPNP_IPPE_SQUARE);

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