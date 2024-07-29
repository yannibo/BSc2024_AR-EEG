using System;
using System.Collections;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Windows.WebCam;

/**
 * Manager that handles camera frame capturing and aruco marker tracking
 * 
 */

public class ArucoMarker {
    public int id;
    public Vector2Int center;
    public Vector2 size;

    public Vector3 position;
    public Quaternion rotation;

    public ArucoMarker(int id, Vector2Int center, Vector2 size, Vector3 position, Quaternion rotation) { 
        this.id = id;
        this.center = center;
        this.size = size;
        this.position = position;
        this.rotation = rotation;
    }
}

public delegate void MarkerPositionUpdate(ArucoMarker marker);

public class ArucoManager : MonoBehaviour {

    public event MarkerPositionUpdate MarkerPositionUpdateEvent;

    // Struct that contains information coming from OpenCV
    [StructLayout(LayoutKind.Sequential)]
    public struct DetectedArucoMarker {
        public int id;
        public Vector2Int center;
        public Vector2 size;
        public Vector3 rvec;
        public Vector3 tvec;
    };

    // Struct that gets passed to the detection thread
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
    };

    // Import the OpenCV Code from the BThesisCV DLL
    [DllImport("BThesisCV.dll")]
    private static extern int FindMarkers(ref Color32[] rawImage, IntPtr detectedMarkers, int maxMarkers, int width, int height, float markerLength);

    // A Reference to the AR Camera
    public Camera viewerCamera;

    // The PhotoCapture Object, which is used to capture frames from the Hololens Camera
    private PhotoCapture photoCaptureObject;

    // The Thread, which is used to call OpenCV Code from
    private Thread imageProcessingThread;

    // A Queue of Actions, which the Main Thread will work on, so that the script can queue actions on the main thread
    private ConcurrentQueue<Action> _mainThreadActions = new ConcurrentQueue<Action>();

    // A Queue used to queue frames for the Image Processing Thread
    private ConcurrentQueue<CameraFrame> _frameQueue = new ConcurrentQueue<CameraFrame>();

    // The selected Resolution for the Hololens camera
    private Vector2Int cameraResolution;

    // A Texture, which will contain the captured frame
    private Texture2D imageTexture;

    // A reference to an Image, which can be used to display the current captured frame
    public RawImage image;

    // A list of all detected aruco markers
    public ArucoMarker[] markers;
    
    // A reference to the prefab, which is used to show detected aruco markers
    public GameObject arucoPrefab;

    // A dictionary containing all instantiated aruco display objects
    public Dictionary<int, ArucoMarkerDisplay> markerDisplays = new Dictionary<int, ArucoMarkerDisplay>();



    private void Start() {
        // Create a PhotoCapture Object
        PhotoCapture.CreateAsync(false, OnPhotoCaptureCreated);
    }

    private void Update() {
        // Take actions from the main thread queue and run them on the main thread
        while (_mainThreadActions.Count > 0) {
            try {
                if (_mainThreadActions.TryDequeue(out Action action)) {
                    action.Invoke();
                }
            } catch (Exception e) {
                // Ignore any Exceptions
            }
        }
    }

    private void OnEnable() {
        // If the image processing thread is already running, stop it and then start it (again)
        if (imageProcessingThread != null) {
            imageProcessingThread.Abort();
        }

        imageProcessingThread = new Thread(ArucoDetection);
        imageProcessingThread.Start();
    }

    private void OnDisable() {
        // Abort the image processing thread in case it is running if this script is disabled
        if (imageProcessingThread == null)
            return;

        imageProcessingThread.Abort();
        imageProcessingThread = null;
    }

    private void OnDestroy() {
        // Destroy the PhotoCapture object if this script is destroyed
        if (photoCaptureObject != null) {
            photoCaptureObject.Dispose();
        }

        // And also stop the image processing thread
        if (imageProcessingThread != null) {
            imageProcessingThread.Abort();
            imageProcessingThread = null;
        }
    }

    /**
     * Shows or hides all aruco marker visualizations
     */
    public void SetArUcoVisible(bool visible) {
        foreach (var marker in markerDisplays.Values)
        {
            marker.gameObject.SetActive(visible);
        }
    }

    private void OnPhotoCaptureCreated(PhotoCapture captureObject) {
        // Abort if there is no camera or the PhotoCapture fails to initialize
        if (captureObject == null) {
            Debug.LogError("Did not find a video capture object. You may not be using the HoloLens.");
            return;
        }

        // Store the PhotoCapture object for later
        photoCaptureObject = captureObject;

        // Setup the Camera Parameters. Hides Holograms in the frames, sets the resolution and pixel format of frames.
        CameraParameters c = new CameraParameters();
        c.hologramOpacity = 0.0f;
        c.cameraResolutionWidth = 1280;
        c.cameraResolutionHeight = 720;
        c.pixelFormat = CapturePixelFormat.BGRA32;

        // Store the selected frame resolution for later
        cameraResolution = new Vector2Int(c.cameraResolutionWidth, c.cameraResolutionHeight);

        // Initialize the Texture2D, which will contain the received frames
        imageTexture = new Texture2D(cameraResolution.x, cameraResolution.y, TextureFormat.BGRA32, false);

        // If the Image is set to an Image, set its Texture and size, so that it will display the received frames
        if (image != null) {
            image.texture = imageTexture;
            image.material.mainTexture = imageTexture;
            image.rectTransform.sizeDelta = new Vector2(cameraResolution.x, cameraResolution.y);
        }

        // Start the Photo Mode
        captureObject.StartPhotoModeAsync(c, OnPhotoModeStarted);
    }

    private void OnPhotoModeStarted(PhotoCapture.PhotoCaptureResult result) {
        // Abort if it wasn't possible to start the PhotoMode
        if (!result.success) {
            Debug.LogError("Unable to start video mode!");
            return;
        }

        // Start the Coroutine, which will start taking frames
        StartCoroutine(TakeImage());
    }

    IEnumerator TakeImage() {
        // Take an image from teh camera every second
        while (true) {
            photoCaptureObject.TakePhotoAsync(onCapturedPhotoToMemoryCallback);
            yield return new WaitForSeconds(1f);
        }
    }

    private void onCapturedPhotoToMemoryCallback(PhotoCapture.PhotoCaptureResult result, PhotoCaptureFrame photoCaptureFrame) {
        // Abort if it wasn't possible to take an image from the camera
        if (!result.success) {
            Debug.Log("Failed to capture frame");
            return;
        }

        // Put frame data into the Texture object
        photoCaptureFrame.UploadImageDataToTexture(imageTexture);

        // Try to get CameraToWorld and Projection Matrices from the Locatable Camera from the Hololens
        Matrix4x4 cameraToWorldMatrix = new Matrix4x4();
        Matrix4x4 projectionMatrix = new Matrix4x4();

        if (photoCaptureFrame.hasLocationData) {
            photoCaptureFrame.TryGetCameraToWorldMatrix(out Matrix4x4 ctwMatrix);
            photoCaptureFrame.TryGetProjectionMatrix(out Matrix4x4 pMatrix);

            cameraToWorldMatrix = ctwMatrix;
            projectionMatrix = pMatrix;
        } else {
            Debug.Log("Could not get Matrices");
        }

        // Setup the Frame Struct, which will be passed to the image processing thread
        CameraFrame cFrame = new CameraFrame();

        // Frame data and image data
        cFrame.photoCaptureFrame = photoCaptureFrame;
        cFrame.imageData = imageTexture.GetPixels32();

        // Location data including the matrices from the Hololens and from the AR camera in the scene
        cFrame.hasLocationData = photoCaptureFrame.hasLocationData;

        // Hololens matrices
        cFrame.cameraToWorldMatrix = cameraToWorldMatrix;
        cFrame.projectionMatrix = projectionMatrix;

        // Scene AR camera matrices
        cFrame.vc_cameraToWorldMatrix = viewerCamera.cameraToWorldMatrix;
        cFrame.vc_projectionMatrix = viewerCamera.projectionMatrix;

        // The offset transform position and rotation
        cFrame.cameraOffsetPos = viewerCamera.transform.parent.position;
        cFrame.cameraOffsetRot = viewerCamera.transform.parent.rotation;

        // Enqueue the currently received frame into the image processing queue
        _frameQueue.Enqueue(cFrame);
    }

    private void ArucoDetection() {
        while (true) {
            try {
                if (_frameQueue.TryDequeue(out CameraFrame cFrame)) {

                    // Call the wrapper for the FindMarkers method from the BThesisCV DLL
                    DetectedArucoMarker[] detectedMarkers = FindMarkersWrapper(cFrame.imageData, cameraResolution.x, cameraResolution.y);
                    markers = new ArucoMarker[detectedMarkers.Length];

                    // Log Markers and their position on the 2D image
                    Debug.Log(detectedMarkers.Length + " Markers found");

                    for (int i = 0; i < detectedMarkers.Length; i++) {
                        Debug.Log("ID: " + detectedMarkers[i].id + " at X: " + detectedMarkers[i].center.x + " Y: " + detectedMarkers[i].center.y);
                    }

                    for (int i = 0; i < detectedMarkers.Length; i++) {
                        DetectedArucoMarker marker = detectedMarkers[i];

                        Vector3 tvec = marker.tvec;
                        tvec.y *= -1f;

                        Quaternion rvec = RotationQuatFromRodrigues(marker.rvec);

                        if (cFrame.hasLocationData) {

                            Matrix4x4 transformUnityCamera = TransformInUnitySpace(tvec, rvec);
                            Matrix4x4 transformUnityWorld = cFrame.cameraToWorldMatrix * transformUnityCamera;

                            tvec = transformUnityWorld.GetColumn(3);
                            tvec += cFrame.cameraOffsetPos;
                            rvec = Quaternion.LookRotation(transformUnityWorld.GetColumn(2), transformUnityWorld.GetColumn(1));

                        } else {

                            Matrix4x4 transformUnityCamera = TransformInUnitySpace(tvec, rvec);
                            Matrix4x4 transformUnityWorld = cFrame.vc_cameraToWorldMatrix * transformUnityCamera;

                            tvec = transformUnityWorld.GetColumn(3);
                            rvec = Quaternion.LookRotation(transformUnityWorld.GetColumn(2), transformUnityWorld.GetColumn(1));
                            /*tvec = UnProjectVector(cFrame.vc_projectionMatrix, tvec);
                            tvec = cFrame.vc_cameraToWorldMatrix.MultiplyPoint(tvec);// + cFrame.cameraOffsetPos;
                            rvec = cFrame.vc_cameraToWorldMatrix.rotation * rvec;*/

                        }

                        markers[i] = new ArucoMarker(marker.id, marker.center, marker.size, tvec, rvec);

                        int index = i;
                        _mainThreadActions.Enqueue(() => {
                            if (markerDisplays.ContainsKey(marker.id)) {
                                markerDisplays[marker.id].transform.SetPositionAndRotation(tvec, rvec);
                            } else {
                                GameObject m = Instantiate(arucoPrefab, tvec, rvec);
                                markerDisplays.Add(marker.id, m.GetComponent<ArucoMarkerDisplay>());
                            }

                            try {
                                MarkerPositionUpdateEvent?.Invoke(markers[index]);
                            } catch (Exception e) {
                                Debug.Log("Error handling Marker Position Update Event: " + e.Message);
                            }
                        });
                    }

                    _frameQueue.Clear();
                    cFrame.photoCaptureFrame.Dispose();
                }
            } catch (ThreadAbortException ex) {
                // This exception is thrown when calling Abort on the thread
                // -> ignore the exception since it is produced on purpose
            }
        }
    }

    // Get a rotation quaternion from rodrigues
    //
    // Copied from https://github.com/doughtmw/ArUcoDetectionHoloLens-Unity/blob/master/ArUcoDetectionHoloLensUnity/Assets/Scripts/CvUtils.cs
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

    // CameraToWorld matrices assume a camera's front direction is in the negative z-direction
    // However, the values obtained from OpenCV assumes the camera's front direction is in the postiive z direction
    // Therefore, we negate the z components of our opencv camera transform
    //
    // Copied from https://github.com/doughtmw/ArUcoDetectionHoloLens-Unity/blob/master/ArUcoDetectionHoloLensUnity/Assets/Scripts/CvUtils.cs
    public Matrix4x4 TransformInUnitySpace(Vector3 v, Quaternion q) {
        var tOpenCV = Matrix4x4.TRS(v, q, Vector3.one);
        var t = tOpenCV;
        t.m20 *= -1.0f;
        t.m21 *= -1.0f;
        t.m22 *= -1.0f;
        t.m23 *= -1.0f;

        return t;
    }

    // Wrapper for the FindMarkers Method from the BThesisCV DLL
    DetectedArucoMarker[] FindMarkersWrapper(Color32[] rawImage, int width, int height) {
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
}
