using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using UnityEngine;
using UnityEngine.UI;

using HoloLensCameraStream;

public class CameraTestNewStream : MonoBehaviour
{

    [DllImport("BThesisCV")]
    private static unsafe extern int FindElectrodes(ref Color32[] rawImage, Vector3* circles, int width, int height, int kernelSize, int dp, int minDist, int param1, int param2, int minRadius, int maxRadius);


    private Texture2D imageTexture;
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

    VideoCapture videoCaptureObject;
    Queue<Action> _mainThreadActions;

    // Start is called before the first frame update
    void Start() {
        _mainThreadActions = new Queue<Action>();

        VideoCapture.CreateAync(OnVideoCaptureCreated);
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

        /*if (electrodeInitializer.electrodes != null && cameraPoints != null) {
            List<Vector3> electrodePositionsVirtual = FindElectrodesVirtual();

            Tuple<Vector3[], double> result = ICP.TestICP(cameraPoints, electrodePositionsVirtual.ToArray());
            foreach (Vector3 pos in result.Item1) {
                GUI.Label(new Rect(pos.x, pos.y, 100, 100), "result");
            }
        }*/

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

    private void Update() {
        lock (_mainThreadActions) {
            while (_mainThreadActions.Count > 0) {
                _mainThreadActions.Dequeue().Invoke();
            }
        }
    }

    private void Enqueue(Action action) {
        lock (_mainThreadActions) {
            _mainThreadActions.Enqueue(action);
        }
    }

    private void OnDestroy() {
        if (videoCaptureObject != null) {
            videoCaptureObject.FrameSampleAcquired -= onFrameReceived;
            videoCaptureObject.Dispose();
        }
    }

    void OnVideoCaptureCreated(VideoCapture captureObject) {
        videoCaptureObject = captureObject;

        if (captureObject == null) {
            Debug.LogError("Did not find a video capture object. You may not be using the HoloLens.");
            return;
        }

        HoloLensCameraStream.Resolution cameraResolution = captureObject.GetSupportedResolutions().OrderByDescending((res) => res.width * res.height).First();
        float cameraFramerate = captureObject.GetSupportedFrameRatesForResolution(cameraResolution).OrderByDescending((res) => res).First();

        captureObject.FrameSampleAcquired += onFrameReceived;

        CameraParameters c = new CameraParameters();
        c.cameraResolutionWidth = cameraResolution.width;
        c.cameraResolutionHeight = cameraResolution.height;
        c.frameRate = Mathf.RoundToInt(cameraFramerate);
        c.pixelFormat = CapturePixelFormat.BGRA32;
        c.rotateImage180Degrees = false;
        c.enableHolograms = false;

        imageTexture = new Texture2D(cameraResolution.width, cameraResolution.height);

        image.texture = imageTexture;
        image.material.mainTexture = imageTexture;
        image.rectTransform.sizeDelta = new Vector2(cameraResolution.width, cameraResolution.height);

        captureObject.StartVideoModeAsync(c, OnVideoModeStarted);
    }

    /*void OnStoppedPhotoMode(PhotoCapture.PhotoCaptureResult result) {
        photoCaptureObject.Dispose();
        photoCaptureObject = null;
    }*/

    private void OnVideoModeStarted(VideoCaptureResult result) {
        if (!result.success) {
            Debug.LogError("Unable to start video mode!");
        }
    }



    byte[] _latestImageBytes;
    private void onFrameReceived(VideoCaptureSample sample) {
        lock (_mainThreadActions) {
            if (_mainThreadActions.Count > 2) {
                sample.Dispose();
                return;
            }
        }

        // allocate byteBuffer
        if (_latestImageBytes == null || _latestImageBytes.Length < sample.dataLength) {
            _latestImageBytes = new byte[sample.dataLength];
        }

        sample.CopyRawImageDataIntoBuffer(_latestImageBytes);
        //sample.UploadImageDataToTexture(imageTexture);

        Enqueue(() => {

            imageTexture.LoadRawTextureData(_latestImageBytes);
            imageTexture.wrapMode = TextureWrapMode.Clamp;
            imageTexture.Apply();

            var rawImage = imageTexture.GetPixels32();

            //// Electrode Finder Code

            Vector3[] circles = FindElectrodesC(rawImage, sample.FrameWidth, sample.FrameHeight);
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

            imageTexture.SetPixels32(rawImage);
            imageTexture.Apply();
        });
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
