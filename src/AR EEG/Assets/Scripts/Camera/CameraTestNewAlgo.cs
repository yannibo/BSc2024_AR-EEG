using System;
using System.Runtime.InteropServices;
using UnityEngine;

using HoloLensCameraStream;
using System.Collections.Generic;
using System.Linq;
using UnityEngine.UI;
using System.Threading;
using System.Collections.Concurrent;

/**
 * Tests with the Hololens Camera Stream Plugin, which was supposed to receiver frames from the Hololens camera faster than the PhotoCapture API, 
 * but it didn't work out that well, because it didn't provide CameraToWorld matrices for the frames.
 * 
 * Most of the code is the same as in ArucoManager.cs
 */


public class CameraTestNewAlgo : MonoBehaviour
{




    [StructLayout(LayoutKind.Sequential)]
    public struct DetectedArucoMarker {
        public int id;
        public Vector2Int center;
        public Vector2 size;
        public Vector3 rvec;
        public Vector3 tvec;
    };


    [DllImport("BThesisCV.dll")]
    private static extern int getSomeInt();

    [DllImport("BThesisCV.dll")]
    //private static extern int FindMarkers(ref byte[] rawImage, IntPtr detectedMarkers, int maxMarkers, int width, int height, float markerLength);
    private static extern int FindMarkers(ref Color32[] rawImage, IntPtr detectedMarkers, int maxMarkers, int width, int height, float markerLength);




    public Camera viewerCamera;
    public GameObject testObjectPrefab;
    private List<GameObject> testObjects = new List<GameObject>();

    private DetectedArucoMarker[] cameraMarkers;
    private Vector2Int cameraResolution;


    private Texture2D imageTexture;
    public RawImage image;

    VideoCapture videoCaptureObject;
    Queue<Action> _mainThreadActions;

    private DateTime startTime;

    int frameCounter = 0;
    /*private ConcurrentStack<VideoCaptureSample> stack = new ConcurrentStack<VideoCaptureSample>();
    private Thread thread;*/

    private void Start() {
        _mainThreadActions = new Queue<Action>();
        VideoCapture.CreateAync(OnVideoCaptureCreated);
    }

    private void Update() {
        //Debug.Log(getSomeInt());

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

   /* private void OnEnable() {
        if (thread != null) {
            thread.Abort();
        }

        thread = new Thread(ArucoDetection);
        thread.Start();
    }

    private void OnDisable() {
        if (thread == null)
            return;

        thread.Abort();
        thread = null;
    }*/

    private void OnDestroy() {
        if (videoCaptureObject != null) {
            videoCaptureObject.FrameSampleAcquired -= onFrameReceived;
            videoCaptureObject.Dispose();
        }
    }


    public string whichMatrix = "";
    private void OnGUI() {
        if (cameraMarkers != null) {
            foreach (DetectedArucoMarker marker in cameraMarkers) {
                GUI.Label(new Rect(marker.center.x, marker.center.y, 100, 100), whichMatrix + " ID: " + marker.id);
            }
        }
    }



    void OnVideoCaptureCreated(VideoCapture captureObject) {
        videoCaptureObject = captureObject;

        if (captureObject == null) {
            Debug.LogError("Did not find a video capture object. You may not be using the HoloLens.");
            return;
        }

        /*HoloLensCameraStream.Resolution cameraResolution = captureObject.GetSupportedResolutions().OrderByDescending((res) => res.width * res.height).First();
        float cameraFramerate = captureObject.GetSupportedFrameRatesForResolution(cameraResolution).OrderByDescending((res) => res).Last();*/

        string tmptext = "RESOLUTIONS:\n";
        foreach (HoloLensCameraStream.Resolution res in captureObject.GetSupportedResolutions().OrderByDescending((res) => res.width * res.height)) {
            foreach (float fps in captureObject.GetSupportedFrameRatesForResolution(res).OrderByDescending((res) => res)) {
                tmptext += res.width + "x" + res.height + ": " + fps + "\n";
            }
        }
        Debug.Log(tmptext);

        captureObject.FrameSampleAcquired += onFrameReceived;

        CameraParameters c = new CameraParameters();
        c.cameraResolutionWidth = 1280;
        c.cameraResolutionHeight = 720;
        c.frameRate = Mathf.RoundToInt(15);
        c.pixelFormat = CapturePixelFormat.BGRA32;
        c.rotateImage180Degrees = true;

        cameraResolution = new Vector2Int(c.cameraResolutionWidth, c.cameraResolutionHeight);

        Enqueue(() => {
            imageTexture = new Texture2D(cameraResolution.x, cameraResolution.y, TextureFormat.BGRA32, false);

            image.texture = imageTexture;
            image.material.mainTexture = imageTexture;
            image.rectTransform.sizeDelta = new Vector2(cameraResolution.x, cameraResolution.y);
        });

        captureObject.StartVideoModeAsync(c, OnVideoModeStarted);
    }

    private void OnVideoModeStarted(VideoCaptureResult result) {
        if (!result.success) {
            Debug.LogError("Unable to start video mode!");
        }
        Debug.LogError("HoloCam 4");
    }

    private void onFrameReceived(VideoCaptureSample sample) {
        if (startTime != null) {
            TimeSpan frameTime = DateTime.Now - startTime;
            double fps = (1 / (frameTime.TotalSeconds));
            Debug.Log("Current FPS: " + fps);
        }
        startTime = DateTime.Now;
        /*if (frameCounter == 15) {
            frameCounter = 0;
        }

        if (frameCounter != 0) {
            frameCounter++;
            return;
        }

        frameCounter++;*/

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

        Matrix4x4 cameraToWorldMatrix = new Matrix4x4();
        Matrix4x4 projectionMatrix = new Matrix4x4();
        bool hasLocatableData = false;

        try {
            sample.TryGetCameraToWorldMatrix(out float[] cam2WorldFloatArr);
            cameraToWorldMatrix = ConvertFloatArrayToMatrix4x4(cam2WorldFloatArr);

            sample.TryGetProjectionMatrix(out float[] projectionFloatArr);
            projectionMatrix = ConvertFloatArrayToMatrix4x4(projectionFloatArr);

            Debug.Log("cameraToWorldMatrix: " + cameraToWorldMatrix + " projectionMatrix: " + projectionMatrix);

            hasLocatableData = true;
        } catch (Exception ex) {
            Debug.Log("Could not get Matrices");
        }

        Enqueue(() => {
            //Debug.Log("latestImageBytes size: " + _latestImageBytes.Length);
            //Debug.Log("imageTexture size: " + imageTexture.GetPixels32().Length);
            imageTexture.LoadRawTextureData(_latestImageBytes);
            imageTexture.wrapMode = TextureWrapMode.Clamp;
            imageTexture.Apply();

            var rawImage = imageTexture.GetPixels32();

            //stack.Push(sample);

            DetectedArucoMarker[] markers = FindMarkersC(rawImage, sample.FrameWidth, sample.FrameHeight);
            cameraMarkers = markers;

            Debug.Log(markers.Length + " Markers found");

            for (int i = 0; i < markers.Length; i++) {
                Debug.Log("ID: " + markers[i].id + " at X: " + markers[i].center.x + " Y: " + markers[i].center.y);
            }

            if (markers.Length > 0) {
                DetectedArucoMarker marker = markers[0];

                Vector3 tvec = marker.tvec;
                tvec.y *= -1;
                tvec.z *= -1;

                Quaternion rvec = RotationQuatFromRodrigues(marker.rvec);

                if (hasLocatableData) { 

                    //Vector3 position = cameraToWorldMatrix.GetColumn(3) - cameraToWorldMatrix.GetColumn(2);
                    //Quaternion rotation = Quaternion.LookRotation(-cameraToWorldMatrix.GetColumn(2), cameraToWorldMatrix.GetColumn(1));


                    Debug.Log("Used Projection Matrix");
                    whichMatrix = "LC";



                    /*var imagePosZeroToOne = new Vector2(pixelPos.x / imageWidth, 1 - (pixelPos.y / imageHeight));
                    var imagePosProjected = (imagePosZeroToOne * 2) - new Vector2(1, 1);    // -1 to 1 space

                    var cameraSpacePos = UnProjectVector(projectionMatrix, new Vector3(imagePosProjected.x, imagePosProjected.y, 1));
                    var worldSpaceCameraPos = cameraToWorldMatrix.MultiplyPoint(Vector3.zero);     // camera location in world space
                    var worldSpaceBoxPos = cameraToWorldMatrix.MultiplyPoint(cameraSpacePos);   // ray point in world space*/

                    tvec = UnProjectVector(projectionMatrix, tvec);
                    tvec = cameraToWorldMatrix.MultiplyPoint(tvec);
                    //tvec = cameraToWorldMatrix * tvec;
                    rvec = cameraToWorldMatrix.rotation * rvec;
                    //rvec = Quaternion.LookRotation(-cameraToWorldMatrix.GetColumn(2), cameraToWorldMatrix.GetColumn(1));

                } else { 
                    whichMatrix = "VC";
                    Debug.Log("Used Viewer Camera");
                    tvec = viewerCamera.cameraToWorldMatrix.MultiplyPoint(tvec);
                    rvec = viewerCamera.cameraToWorldMatrix.rotation * rvec;
                }

                //sample.Dispose();

                //Enqueue(() => {
                    /*imageTexture.LoadRawTextureData(_latestImageBytes);
                    imageTexture.wrapMode = TextureWrapMode.Clamp;
                    imageTexture.Apply();*/


                    if (testObjects.Count == 0) {
                        testObjects.Add(Instantiate(testObjectPrefab, tvec, rvec));
                    } else {
                        testObjects[0].transform.SetPositionAndRotation(tvec, rvec);
                    }
               // });
            }



            imageTexture.SetPixels32(rawImage);
            imageTexture.Apply();


            /*
            Debug.LogError("HoloCam 10");*/
        });
    }


    byte[] _latestImageBytes;
    /*void ArucoDetection() {

        while (true) {
            try {
                if (stack.TryPop(out VideoCaptureSample sample)) {

                    if (_latestImageBytes == null || _latestImageBytes.Length < sample.dataLength) {
                        _latestImageBytes = new byte[sample.dataLength];
                    }

                    sample.CopyRawImageDataIntoBuffer(_latestImageBytes);

                    imageTexture.LoadRawTextureData(_latestImageBytes);
                    imageTexture.wrapMode = TextureWrapMode.Clamp;
                    imageTexture.Apply();

                    var rawImage = imageTexture.GetPixels32();

                    DetectedArucoMarker[] markers = FindMarkersC(rawImage, sample.FrameWidth, sample.FrameHeight);
                    cameraMarkers = markers;

                    Debug.Log(markers.Length + " Markers found");

                    for (int i = 0; i < markers.Length; i++) {
                        Debug.Log("ID: " + markers[i].id + " at X: " + markers[i].center.x + " Y: " + markers[i].center.y);
                    }

                    if (markers.Length > 0) {
                        DetectedArucoMarker marker = markers[0];

                        Vector3 tvec = marker.tvec;
                        tvec.y *= -1;

                        Quaternion rvec = RotationQuatFromRodrigues(marker.rvec);

                        if (sample.hasLocationData) {
                            sample.TryGetCameraToWorldMatrix(out float[] cam2WorldFloatArr);

                            Matrix4x4 cameraToWorldMatrix = ConvertFloatArrayToMatrix4x4(cam2WorldFloatArr);

                            Vector3 position = cameraToWorldMatrix.GetColumn(3) - cameraToWorldMatrix.GetColumn(2);
                            Quaternion rotation = Quaternion.LookRotation(-cameraToWorldMatrix.GetColumn(2), cameraToWorldMatrix.GetColumn(1));

                            sample.TryGetProjectionMatrix(out float[] projectionFloatArr);
                            Matrix4x4 projectionMatrix = ConvertFloatArrayToMatrix4x4(projectionFloatArr);

                            Debug.Log("Used Projection Matrix");
                            whichMatrix = "LC";
                            tvec = tvec + position;
                            rvec = rvec * rotation;

                        } else {
                            whichMatrix = "VC";
                            Debug.Log("Used Viewer Camera");
                            tvec = viewerCamera.transform.TransformPoint(tvec);
                            rvec = viewerCamera.transform.rotation * rvec;
                        }

                        sample.Dispose();

                        Enqueue(() => {
                            imageTexture.LoadRawTextureData(_latestImageBytes);
                            imageTexture.wrapMode = TextureWrapMode.Clamp;
                            imageTexture.Apply();


                            if (testObjects.Count == 0) {
                                testObjects.Add(Instantiate(testObjectPrefab, tvec, rvec));
                            } else {
                                testObjects[0].transform.SetPositionAndRotation(tvec, rvec);
                            }
                        });
                    }
                }

                // Erase older data
                stack.Clear();
            } catch (ThreadAbortException ex) {
                // This exception is thrown when calling Abort on the thread
                // -> ignore the exception since it is produced on purpose
            }
        }
    }*/


    public static Vector3 UnProjectVector(Matrix4x4 proj, Vector3 to) {
        Vector3 from = new Vector3(0, 0, 0);
        var axsX = proj.GetRow(0);
        var axsY = proj.GetRow(1);
        var axsZ = proj.GetRow(2);
        from.z = to.z / axsZ.z;
        from.y = (to.y - (from.z * axsY.z)) / axsY.y;
        from.x = (to.x - (from.z * axsX.z)) / axsX.x;
        return from;
    }

    DetectedArucoMarker[] FindMarkersC(Color32[] rawImage, int width, int height) {
        int structSize = Marshal.SizeOf(typeof(DetectedArucoMarker));
        IntPtr ptr = Marshal.AllocHGlobal(50 * structSize);

        int n = -1;
        n = FindMarkers(ref rawImage, ptr, 50, width, height, 0.01f);

        DetectedArucoMarker[] detectedMarkers = new DetectedArucoMarker[n];

        for (int i = 0; i < n; i++) {
            IntPtr structPtr = new IntPtr(ptr.ToInt64() + i * structSize);
            detectedMarkers[i] = Marshal.PtrToStructure<DetectedArucoMarker>(structPtr);
        }

        Marshal.FreeHGlobal(ptr);

        /*int n = -1;
        unsafe {
            fixed (DetectedArucoMarker* vecPtr = detectedMarkers) {
                n = FindMarkers(ref rawImage, vecPtr, 50, width, height);
            }
        }*/

        Debug.Log("Done with OpenCV Markers: " + n);

        /*Vector3[] c = new Vector3[n];
        for (int i = 0; i < n; i++) {
            c[i] = new Vector3(circles[i].x / width, circles[i].y / height);
        }*/

        return detectedMarkers;
    }

    // CameraToWorld matrices assume a camera's front direction is in the negative z-direction
    // However, the values obtained from OpenCV assumes the camera's front direction is in the postiive z direction
    // Therefore, we negate the z components of our opencv camera transform
    public Matrix4x4 TransformInUnitySpace(Vector3 v, Quaternion q) {
        var tOpenCV = Matrix4x4.TRS(v, q, Vector3.one);
        var t = tOpenCV;
        t.m20 *= -1.0f;
        t.m21 *= -1.0f;
        t.m22 *= -1.0f;
        t.m23 *= -1.0f;

        return t;
    }

    // Convert from system numerics to unity matrix 4x4
    public Matrix4x4 Mat4x4FromFloat4x4(System.Numerics.Matrix4x4 m) {
        return new Matrix4x4() {
            m00 = m.M11,
            m10 = m.M21,
            m20 = m.M31,
            m30 = m.M41,

            m01 = m.M12,
            m11 = m.M22,
            m21 = m.M32,
            m31 = m.M42,

            m02 = m.M13,
            m12 = m.M23,
            m22 = m.M33,
            m32 = m.M43,

            m03 = m.M14,
            m13 = m.M24,
            m23 = m.M34,
            m33 = m.M44,
        };
    }

    // Get a rotation quaternion from rodrigues
    public Quaternion RotationQuatFromRodrigues(Vector3 v) {
        var angle = Mathf.Rad2Deg * v.magnitude;
        var axis = v.normalized;
        Quaternion q = Quaternion.AngleAxis(angle, axis);

        // Ensure: 
        // Positive x axis is in the left direction of the observed marker
        // Positive y axis is in the upward direction of the observed marker
        // Positive z axis is facing outward from the observed marker
        // Convert from rodrigues to quaternion representation of angle
        q = Quaternion.Euler(
            -1.0f * q.eulerAngles.x,
            q.eulerAngles.y,
            -1.0f * q.eulerAngles.z) * Quaternion.Euler(0, 0, 180);

        return q;
    }

    /// <summary>
    /// Helper method for converting into UnityEngine.Matrix4x4
    /// </summary>
    /// <param name="matrixAsArray"></param>
    /// <returns></returns>
    public static Matrix4x4 ConvertFloatArrayToMatrix4x4(float[] matrixAsArray) {
        //There is probably a better way to be doing this but System.Numerics.Matrix4x4 is not available 
        //in Unity and we do not include UnityEngine in the plugin.
        Matrix4x4 m = new Matrix4x4();
        m.m00 = matrixAsArray[0];
        m.m01 = matrixAsArray[1];
        m.m02 = matrixAsArray[2];
        m.m03 = matrixAsArray[3];
        m.m10 = matrixAsArray[4];
        m.m11 = matrixAsArray[5];
        m.m12 = matrixAsArray[6];
        m.m13 = matrixAsArray[7];
        m.m20 = matrixAsArray[8];
        m.m21 = matrixAsArray[9];
        m.m22 = matrixAsArray[10];
        m.m23 = matrixAsArray[11];
        m.m30 = matrixAsArray[12];
        m.m31 = matrixAsArray[13];
        m.m32 = matrixAsArray[14];
        m.m33 = matrixAsArray[15];

        return m;
    }

}
