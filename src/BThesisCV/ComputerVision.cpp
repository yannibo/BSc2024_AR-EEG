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

template struct std::vector<Vec3f>;

extern "C"
{

	__declspec(dllexport) void ProcessImage(Color32** rawImage, int width, int height)
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

	__declspec(dllexport) int FindElectrodes(Color32** rawImage, Vector3* circles, int width, int height, int kernelSize, int dp, int minDist, int param1, int param2, int minRadius, int maxRadius)
	{

		// create an opencv object sharing the same data space
		Mat image(height, width, CV_8UC4, *rawImage);

		// start with flip (in both directions) if your image looks inverted
		//flip(image, image, -1);
		flip(image, image, 0);

		// start processing the image
		// ************************************************
		Mat gray(height, width, CV_8UC1);
		cvtColor(image, gray, ColorConversionCodes::COLOR_BGR2GRAY);
		//imshow("gray", gray);

		Mat blur(height, width, CV_8UC1);
		medianBlur(gray, blur, 11);
		//imshow("blur", blur);

		Mat thresh(height, width, CV_8UC1);
		threshold(blur, thresh, 140, 255, ThresholdTypes::THRESH_BINARY);
		//imshow("threshold", thresh);

		Mat kernel = getStructuringElement(MorphShapes::MORPH_ELLIPSE, Size(kernelSize, kernelSize));
		
		Mat opening(height, width, CV_8UC1);
		morphologyEx(thresh, opening, MorphTypes::MORPH_OPEN, kernel, Point(-1, -1), 3);
		//imshow("opening", opening);

		Mat dila(height, width, CV_8UC1);
		dilate(opening, dila, NULL, Point(-1, -1), 2);
		imshow("dila", dila);

		//std::vector<float> circles;
		std::vector<Vec3f> cir;
		HoughCircles(dila, cir, HoughModes::HOUGH_GRADIENT, dp, minDist, param1, param2, minRadius, maxRadius);

		for (int i = 0; i < cir.size(); i++) {
			circles[i].x = cir[i][0];
			circles[i].y = cir[i][1];
			circles[i].z = cir[i][2];

			circle(image, Point(cir[i][0], cir[i][1]), cir[i][2], Scalar((double)255, (double)0, (double)255), 3);
		}

		// end processing the image
		// ************************************************

		// flip again (just vertically) to get the right orientation
		//flip(image, image, 0);
		flip(image, image, 0);
		//return circles.;
		return cir.size();
	}
}