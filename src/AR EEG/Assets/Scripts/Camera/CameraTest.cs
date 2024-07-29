using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Windows.WebCam;

/**
 * First tests with PhotoCapture and Electrode detection with the ICP algorithm and the detection of electrodes from the received camera frame
 */
public class CameraTest : MonoBehaviour
{

    [DllImport("BThesisCV")]
    private static unsafe extern int FindElectrodes(ref Color32[] rawImage, Vector3* circles, int width, int height, int kernelSize, int dp, int minDist, int param1, int param2, int minRadius, int maxRadius);


    private Texture2D Texture2D;
    public RawImage image;
    public ElectrodeInitializer electrodeInitializer;
    public Camera viewerCamera;
    public GameObject testObjectPrefab;
    private List<GameObject> testObjects = new List<GameObject>();

    private Vector3[] cameraPoints;

    public int kernelSize = 5;
    public int dp = 2;
    public int minDist = 50;
    public int param1 = 100;
    public int param2 = 40;
    public int minRadius = 10;
    public int maxRadius = 50;

    // Start is called before the first frame update
    void Start()
    {
        PhotoCapture.CreateAsync(false, OnPhotoCaptureCreated);
    }


    private void OnGUI() {
        if (electrodeInitializer.electrodes != null) {
            List<Vector3> electrodePositionsVirtual = FindElectrodesVirtual();

            foreach (Vector3 pos in electrodePositionsVirtual) {
                GUI.Label(new Rect(pos.x * Screen.width, pos.y * Screen.height, 100, 100), "virtual");
            }
        }

        if (cameraPoints != null) {
            foreach (Vector3 pos in cameraPoints) {
                GUI.Label(new Rect(pos.x * Screen.width, pos.y * Screen.height, 100, 100), "camera");
            }
        }

        if (electrodeInitializer.electrodes != null && cameraPoints != null) {
            List<Vector3> electrodePositionsVirtual = FindElectrodesVirtual();

            Tuple<Vector3[], double> newPoints = ICP.TestICP(cameraPoints, electrodePositionsVirtual.ToArray());
            //Debug.Log("New Point Error: " + newPoints.Item2 + " | " + (newPoints.Item2 <= 150000));
            if (newPoints.Item2 <= 150000) {
                foreach (Vector3 pos in newPoints.Item1) {
                    //Debug.Log("New Point");

                    //Debug.Log("1:" + pos.x + "|" + pos.y);
                    /*float screenX = (pos.x / 640) * Screen.width;
                    float screenY = (pos.y / 480) * Screen.height;

                    Debug.Log("2: " + screenX + "|" + screenY);*/

                    GUI.Label(new Rect(pos.x * Screen.width, pos.y * Screen.height, 100, 100), "result");
                }
            }
        }
    }

    /**
     * Stuff to take images from the hololens camera
     * Take a look at ArucoManager.cs for better documentation on essentially the same stuff
     */

    private PhotoCapture photoCaptureObject = null;

    void OnPhotoCaptureCreated(PhotoCapture captureObject) {
        photoCaptureObject = captureObject;

        Resolution cameraResolution = PhotoCapture.SupportedResolutions.OrderByDescending((res) => res.width * res.height).First();

        CameraParameters c = new CameraParameters();
        c.hologramOpacity = 0.0f;
        c.cameraResolutionWidth = cameraResolution.width;
        c.cameraResolutionHeight = cameraResolution.height;
        c.pixelFormat = CapturePixelFormat.BGRA32;

        captureObject.StartPhotoModeAsync(c, OnPhotoModeStarted);
    }

    void OnStoppedPhotoMode(PhotoCapture.PhotoCaptureResult result) {
        photoCaptureObject.Dispose();
        photoCaptureObject = null;
    }

    private void OnPhotoModeStarted(PhotoCapture.PhotoCaptureResult result) {
        if (result.success) {

            Resolution cameraResolution = PhotoCapture.SupportedResolutions.OrderByDescending((res) => res.width * res.height).First();
            Texture2D = new Texture2D(cameraResolution.width, cameraResolution.height);

            image.texture = Texture2D;
            image.material.mainTexture = Texture2D;
            image.rectTransform.sizeDelta = new Vector2(cameraResolution.width, cameraResolution.height);

            //photoCaptureObject.TakePhotoAsync(onCapturedPhotoToMemoryCallback);
            StartCoroutine(TakeImage());
        } else {
            Debug.LogError("Unable to start photo mode!");
        }
    }

    IEnumerator TakeImage() {
        while (true) {
            photoCaptureObject.TakePhotoAsync(onCapturedPhotoToMemoryCallback);
            yield return new WaitForSeconds(.1f);
        }
    }

    /**
     * Feeds the camera frame into OpenCV to detect electrodes and then run the ICP algorithm to try to assign electrodes their labels.
     */

    private void onCapturedPhotoToMemoryCallback(PhotoCapture.PhotoCaptureResult result, PhotoCaptureFrame photoCaptureFrame) {
        if (result.success) {
            Resolution cameraResolution = PhotoCapture.SupportedResolutions.OrderByDescending((res) => res.width * res.height).First();

            Texture2D tmpText = new Texture2D(cameraResolution.width, cameraResolution.height, TextureFormat.BGRA32, false);
            photoCaptureFrame.UploadImageDataToTexture(tmpText);

            var rawImage = tmpText.GetPixels32();

            //// Electrode Finder Code

            Vector3[] circles = FindElectrodesC(rawImage, cameraResolution.width, cameraResolution.height);
            cameraPoints = circles;

            Debug.Log(circles.Length + " Circles found");
            Debug.Log(circles);

            if (electrodeInitializer.electrodes != null && cameraPoints != null) {
                List<Vector3> electrodePositionsVirtual = FindElectrodesVirtual();
                //130183

                Tuple<Vector3[], double> newPoints = ICP.TestICP(cameraPoints, electrodePositionsVirtual.ToArray());
                Debug.Log("New Point Error: " + newPoints.Item2 + " | " + (newPoints.Item2 <= 0.45));
                if (newPoints.Item2 <= 0.45) {

                    foreach (GameObject obj in testObjects) {
                        Destroy(obj);
                    }

                    testObjects.Clear();
                    foreach (Vector3 pos in newPoints.Item1) {
                        Debug.Log("New Point");

                        float screenX = pos.x * viewerCamera.pixelWidth;
                        float screenY = (1 - pos.y) * viewerCamera.pixelHeight;

                        //Debug.Log(screenX + "|" + screenY);

                        Vector3 point = viewerCamera.ScreenToWorldPoint(new Vector3(screenX, screenY, 1));

                        Debug.DrawLine(viewerCamera.transform.position, point, Color.magenta, 5);

                        int layerMask = LayerMask.GetMask("Head");
                        RaycastHit hit;
                        bool didHit = Physics.Raycast(viewerCamera.transform.position, point - viewerCamera.transform.position, out hit, 1000, layerMask);
                        Debug.Log(didHit);
                        if (didHit) {
                            Debug.DrawLine(viewerCamera.transform.position, hit.point, Color.green, 30);
                            GameObject test = Instantiate(testObjectPrefab, hit.point, Quaternion.identity);
                            testObjects.Add(test);
                        }
                    }
                }
            }

            //// Apply Texture

            Texture2D.SetPixels32(rawImage);
            Texture2D.Apply();

            Debug.Log("Took Photo");
        } else {
            Debug.LogError("Unable to capture photo");
        }
    }

    Vector3[] FindElectrodesC(Color32[] rawImage, int width, int height) {
        Vector3[] circles = new Vector3[1000];
        int n = -1;
        unsafe {
            fixed (Vector3* vecPtr = circles) {
                n = FindElectrodes(ref rawImage, vecPtr, width, height, kernelSize, dp, minDist, param1, param2, minRadius, maxRadius);
            }
        }

        Vector3[] c = new Vector3[n];
        for (int i = 0; i < n; i++) {
            //c[i] = circles[i];
            //Debug.Log(circles[i].x + "|" + circles[i].x / width + "," + circles[i].y + "|" + circles[i].y / height);
            c[i] = new Vector3(circles[i].x / width, circles[i].y / height);
        }

        return c;
    }

    /**
     * Methods that were used to get screen space coordinates of the electrodes in the scene for the ICP algorithm.
     */

    List<Vector3> FindElectrodesVirtual() {
        List<Vector3> electrodePositions = new List<Vector3>();

        Matrix4x4 matrix = viewerCamera.projectionMatrix * viewerCamera.worldToCameraMatrix;

        foreach (var electrode in electrodeInitializer.electrodes) {
            if (!electrode.gameObject.activeSelf)
                continue;

            Vector3 screenPos = matrix.MultiplyPoint(electrode.transform.position);

            screenPos = new Vector3(screenPos.x + 1f, screenPos.y + 1f, screenPos.z + 1f) / 2f;
            /*screenPos = new Vector3(screenPos.x * Screen.width, screenPos.y * Screen.height, screenPos.z);

            float screenX = screenPos.x / Screen.width;
            float screenY = 1 - (screenPos.y / Screen.height);*/

            screenPos = new Vector3(screenPos.x * viewerCamera.pixelWidth, screenPos.y * viewerCamera.pixelHeight, screenPos.z);

            float screenX = screenPos.x / viewerCamera.pixelWidth;
            float screenY = 1 - (screenPos.y / viewerCamera.pixelHeight);

            //Debug.Log(electrode.GetComponent<ElectrodeDisplay>().channelName + ": " + screenX + "|" + screenY);

            electrodePositions.Add(new Vector3(screenX, screenY, 0));
        }

        return electrodePositions;
    }

    /*List<Vector3> FindElectrodesVirtual() {
        List<Vector3> electrodePositions = new List<Vector3>();

        Matrix4x4 matrix = viewerCamera.projectionMatrix * viewerCamera.worldToCameraMatrix;

        foreach (var electrode in electrodeInitializer.electrodes) {
            if (!electrode.gameObject.activeSelf)
                continue;

            Vector3 screenPos = matrix.MultiplyPoint(electrode.transform.position);

            screenPos = new Vector3(screenPos.x + 1f, screenPos.y + 1f, screenPos.z + 1f) / 2f;

            screenPos = new Vector3(screenPos.x * Screen.width, screenPos.y * Screen.height, screenPos.z);
            //var unityScreenPos = new Rect(screenPos.x, Screen.height - screenPos.y, 100, 100);

            float screenX = (screenPos.x / Screen.width) * 640;
            float screenY = (1 - (screenPos.y / Screen.height)) * 480;

            electrodePositions.Add(new Vector3(screenX, screenY, 0));
        }

        return electrodePositions;
    }

    List<Vector3> FindElectrodesVirtualScreen() {
        List<Vector3> electrodePositions = new List<Vector3>();

        Matrix4x4 matrix = viewerCamera.projectionMatrix * viewerCamera.worldToCameraMatrix;

        foreach (var electrode in electrodeInitializer.electrodes) {
            if (!electrode.gameObject.activeSelf)
                continue;

            Vector3 screenPos = matrix.MultiplyPoint(electrode.transform.position);

            screenPos = new Vector3(screenPos.x + 1f, screenPos.y + 1f, screenPos.z + 1f) / 2f;
            screenPos = new Vector3(screenPos.x * Screen.width, screenPos.y * Screen.height, screenPos.z);
            
            electrodePositions.Add(screenPos);
        }

        return electrodePositions;
    }*/
}
