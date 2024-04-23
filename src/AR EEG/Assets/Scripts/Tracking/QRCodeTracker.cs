using Microsoft.MixedReality.OpenXR;
using Microsoft.MixedReality.QR;
using MixedReality.Toolkit;
using UnityEngine;

/**
 * QR Code Tracker takes a QR Code GUID and then tracks this QR Code in the world
 */
public class QRCodeTracker : MonoBehaviour {

    // Te QR Code that this Tracker has to track
    private QRCode code;

    // The Camera of the device to be able to position the QR Code in world space
    private Camera viewerCamera;

    // The SpatialGraphNode of the QRcode this tracker tracks
    private SpatialGraphNode node;

    // The Transform of the Child GameObjects, which is needed to adjust to QRCode size
    [SerializeField]
    private Transform childPosition;

    // A Reference to the Transform of the QR Code Origin Marker
    [SerializeField]
    private Transform qrOrigin;

    // Save the original child Offset to apply it on the head when tracking
    private Vector3 originPositionOffset;
    private Quaternion originRotationOffset;

    private void Start() {
        originPositionOffset = qrOrigin.localPosition;
        originRotationOffset = qrOrigin.rotation;

        //Debug.Log(originPositionOffset);
    }

    void Update() {
        // Check whether a QRCode has already been assigned to this tracker
        if (node != null) {

            // Locate the QRCode with the help of the SpatialGraphNode
            Pose pose;
            if (node.TryLocate(FrameTime.OnUpdate, out pose)) {

                // Transform the position into world space
                pose = pose.GetTransformedBy(viewerCamera.transform.parent);


                // Apply new position to the Transform
                transform.position = pose.position;
                transform.rotation = pose.rotation * Quaternion.Euler(180, 0, 0);// * Quaternion.Inverse(originRotationOffset);
                //transform.rotation.SetAxisAngle(new Vector3(0, 0, 1), 180);
                //transform.rotation *= Quaternion.AngleAxis(180, new Vector3(0, 0, 1));

                transform.rotation *= Quaternion.Inverse(originRotationOffset);

                Vector3 posDiff = transform.position - transform.TransformPoint(originPositionOffset);
                transform.position += posDiff;


                /*Debug.Log(originPositionOffset);
                Debug.Log(pose.position);
                Debug.Log(transform.TransformPoint(originPositionOffset));*/
            }
        }
    }

    /**
     * Method to assign a QRCode to this tracker
     */
    public void SetCode(QRCode code, Camera camera) {
        this.code = code;
        this.viewerCamera = camera;

        // Acquire the SpatialGraphNode for the given QRCode
        node = SpatialGraphNode.FromStaticNodeId(code.SpatialGraphNodeId);
        //Debug.Log(node);

        // Adjust childtransform to the Size of the QRCode
        Vector3 child = childPosition.position;
        child.x += (code.PhysicalSideLength * 1f) / 2f;
        childPosition.position = child;
    }
}
