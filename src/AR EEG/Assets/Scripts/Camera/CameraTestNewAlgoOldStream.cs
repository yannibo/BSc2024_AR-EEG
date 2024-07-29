using System;
using System.Runtime.InteropServices;
using UnityEngine;

using System.Collections.Generic;
using System.Linq;
using UnityEngine.UI;
using UnityEngine.Windows.WebCam;
using System.Collections;
using System.Collections.Concurrent;
using System.Threading;
using MixedReality.Toolkit;

/**
 * These were the last tests, but with the PhotoCapture API again. This time the image processing had a separate thread for it. 
 * This is the "unclean" version of ArucoManager.cs, which has better documentation.
 */

public class CameraTestNewAlgoOldStream : MonoBehaviour
{


    /**
     * A struct defining the data type of the data, BThesisCV returns for each detected ArUco marker
     */

    [StructLayout(LayoutKind.Sequential)]
    public struct DetectedArucoMarker {
        public int id;
        public Vector2Int center;
        public Vector2 size;
        public Vector3 rvec;
        public Vector3 tvec;
    };

    /**
     * A struct used to pass data into a separate thread for aruco detection.
     */
    public struct CameraFrame {
        public PhotoCaptureFrame photoCaptureFrame;
        public Color32[] imageData;
        public bool hasLocationData;
        public Matrix4x4 cameraToWorldMatrix;
        public Matrix4x4 projectionMatrix;
        public Matrix4x4 vc_cameraToWorldMatrix;
        public Matrix4x4 vc_projectionMatrix;
        public Vector3 cameraOffsetPos;
        public Quaternion cameraOffsetRot;
        public Vector3 cameraPosition;
        public Quaternion cameraRotation;
    };


    /**
     * DLL method imports from BThesisCV
     */
    /*[DllImport("BThesisCV.dll")]
    private static extern int getSomeInt();*/

    [DllImport("BThesisCV.dll")]
    //private static extern int FindMarkers(ref byte[] rawImage, IntPtr detectedMarkers, int maxMarkers, int width, int height, float markerLength);
    private static extern int FindMarkers(ref Color32[] rawImage, IntPtr detectedMarkers, int maxMarkers, int width, int height, float markerLength);

    // A reference to the camera in unity
    public Camera viewerCamera;
    public GameObject testObjectPrefab;
    private List<GameObject> testObjects = new List<GameObject>();

    private DetectedArucoMarker[] cameraMarkers;
    private Vector2Int cameraResolution;

    private Texture2D imageTexture;
    public RawImage image;

    PhotoCapture photoCaptureObject;
    Queue<Action> _mainThreadActions;

    int frameCounter = 0;
    private ConcurrentStack<CameraFrame> stack = new ConcurrentStack<CameraFrame>();
    private Thread thread;

    private DateTime startTime;

    private void Start() {
        _mainThreadActions = new Queue<Action>();
        PhotoCapture.CreateAsync(false, OnPhotoCaptureCreated);
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

    private void OnEnable() {
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
    }

    private void OnDestroy() {
        if (photoCaptureObject != null) {
            photoCaptureObject.Dispose();
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



    void OnPhotoCaptureCreated(PhotoCapture captureObject) {
        photoCaptureObject = captureObject;

        if (captureObject == null) {
            Debug.LogError("Did not find a video capture object. You may not be using the HoloLens.");
            return;
        }

        Resolution resolution = PhotoCapture.SupportedResolutions.OrderByDescending((res) => res.width * res.height).Last();

        string tmptext = "RESOLUTIONS:\n";
        foreach (Resolution res in PhotoCapture.SupportedResolutions.OrderByDescending((res) => res.width * res.height)) {
            tmptext += res.width + "x" + res.height + "\n";
        }
        Debug.Log(tmptext);


        CameraParameters c = new CameraParameters();
        c.hologramOpacity = 0.0f;
        //c.cameraResolutionWidth = cameraResolution.width;
        //c.cameraResolutionHeight = cameraResolution.height;
        c.cameraResolutionWidth = 1280;//resolution.width;
        c.cameraResolutionHeight = 720;//resolution.height;
        c.pixelFormat = CapturePixelFormat.BGRA32;

        cameraResolution = new Vector2Int(c.cameraResolutionWidth, c.cameraResolutionHeight);

        //Enqueue(() => {
            imageTexture = new Texture2D(cameraResolution.x, cameraResolution.y, TextureFormat.BGRA32, false);

            image.texture = imageTexture;
            image.material.mainTexture = imageTexture;
            image.rectTransform.sizeDelta = new Vector2(cameraResolution.x, cameraResolution.y);
        //});

        captureObject.StartPhotoModeAsync(c, OnPhotoModeStarted);
    }

    private void OnPhotoModeStarted(PhotoCapture.PhotoCaptureResult result) {
        if (!result.success) {
            Debug.LogError("Unable to start video mode!");
            return;
        }
        StartCoroutine(TakeImage());
    }

    IEnumerator TakeImage() {
        while (true) {
            startTime = DateTime.Now;
            photoCaptureObject.TakePhotoAsync(onCapturedPhotoToMemoryCallback);
            yield return new WaitForSeconds(3f);
        }
    }

    private void onCapturedPhotoToMemoryCallback(PhotoCapture.PhotoCaptureResult result, PhotoCaptureFrame photoCaptureFrame) {

        TimeSpan difference = DateTime.Now - startTime;
        Debug.Log("Took " + difference.TotalMilliseconds + " ms to take photo");

        if (!result.success) {
            Debug.Log("Failed1");
            return;
        }

        /*lock (_mainThreadActions) {
            if (_mainThreadActions.Count > 2) {
                return;
            }
        }*/

        //Resolution cameraResolution = PhotoCapture.SupportedResolutions.OrderByDescending((res) => res.width * res.height).First();

        //Texture2D tmpText = new Texture2D(cameraResolution.width, cameraResolution.height, TextureFormat.BGRA32, false);
        photoCaptureFrame.UploadImageDataToTexture(imageTexture);


        Matrix4x4 cameraToWorldMatrix = new Matrix4x4();
        Matrix4x4 projectionMatrix = new Matrix4x4();

        if (photoCaptureFrame.hasLocationData) {
            photoCaptureFrame.TryGetCameraToWorldMatrix(out Matrix4x4 ctwMatrix);
            photoCaptureFrame.TryGetProjectionMatrix(out Matrix4x4 pMatrix);

            cameraToWorldMatrix = ctwMatrix;
            projectionMatrix = pMatrix;

            //Debug.Log("cameraToWorldMatrix: " + cameraToWorldMatrix + " projectionMatrix: " + projectionMatrix);
        } else {
            Debug.Log("Could not get Matrices");
        }
        Debug.Log("cameraToWorldMatrix: " + viewerCamera.cameraToWorldMatrix + " projectionMatrix: " + viewerCamera.projectionMatrix);

        CameraFrame cFrame = new CameraFrame();
        cFrame.photoCaptureFrame = photoCaptureFrame;
        cFrame.imageData = imageTexture.GetPixels32();

        cFrame.hasLocationData = photoCaptureFrame.hasLocationData;
        cFrame.cameraToWorldMatrix = cameraToWorldMatrix;
        cFrame.vc_cameraToWorldMatrix = viewerCamera.cameraToWorldMatrix;

        cFrame.projectionMatrix = projectionMatrix;
        cFrame.vc_projectionMatrix = viewerCamera.projectionMatrix;

        cFrame.cameraOffsetPos = viewerCamera.transform.parent.position;
        cFrame.cameraOffsetRot = viewerCamera.transform.parent.rotation;
        //cFrame.cameraOffset = viewerCamera.transform.parent;
        cFrame.cameraPosition = viewerCamera.transform.position;
        cFrame.cameraRotation = viewerCamera.transform.rotation;

        stack.Push(cFrame);
    }

    /**
     * Loop for the ArUco detection thread that takes image samples from a stack and runs the aruco detection on it.
     */
    void ArucoDetection() {

        while (true) {
            try {
                if (stack.TryPop(out CameraFrame cFrame)) {

                    var rawImage = cFrame.imageData;

                    DetectedArucoMarker[] markers = FindMarkersC(rawImage, cameraResolution.x, cameraResolution.y);
                    cameraMarkers = markers;

                    Debug.Log(markers.Length + " Markers found");

                    for (int i = 0; i < markers.Length; i++) {
                        Debug.Log("ID: " + markers[i].id + " at X: " + markers[i].center.x + " Y: " + markers[i].center.y);
                    }

                    if (markers.Length > 0) {
                        DetectedArucoMarker marker = markers[0];

                        Vector3 tvec = marker.tvec;
                        tvec.y *= -1f;
                        //tvec.z *= -1;

                        Quaternion rvec = RotationQuatFromRodrigues(marker.rvec);

                        if (cFrame.hasLocationData) {
                            Debug.Log("Used Projection Matrix");

                            Matrix4x4 transformUnityCamera = TransformInUnitySpace(tvec, rvec);
                            Matrix4x4 transformUnityWorld = cFrame.cameraToWorldMatrix * transformUnityCamera;

                            tvec = transformUnityWorld.GetColumn(3);
                            tvec += cFrame.cameraOffsetPos;
                            rvec = Quaternion.LookRotation(transformUnityWorld.GetColumn(2), transformUnityWorld.GetColumn(1));

                        } else {
                            Debug.Log("Used Viewer Camera");

                            tvec = UnProjectVector(cFrame.vc_projectionMatrix, tvec);
                            tvec = cFrame.vc_cameraToWorldMatrix.MultiplyPoint(tvec);
                            rvec = cFrame.vc_cameraToWorldMatrix.rotation * rvec;
                        }

                        Enqueue(() => {
                            if (testObjects.Count == 0) {
                                testObjects.Add(Instantiate(testObjectPrefab, tvec, rvec));
                            } else {
                                testObjects[0].transform.SetPositionAndRotation(tvec, rvec);
                            }
                        });
                    }

                    stack.Clear();
                    cFrame.photoCaptureFrame.Dispose();
                } else {
                    //Debug.Log("No Pop");
                }

                // Erase older data
            } catch (ThreadAbortException ex) {
                // This exception is thrown when calling Abort on the thread
                // -> ignore the exception since it is produced on purpose
            }
        }
    }


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

    /**
     * A wrapper for the FindMarkers method of BThesisCV. Handles passing data to it and acquiring the results
     */
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
