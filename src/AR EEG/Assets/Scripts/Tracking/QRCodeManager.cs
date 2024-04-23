using Microsoft.MixedReality.QR;
using System;
using System.Collections.Generic;
using UnityEngine;

/**
 * QRCodeManager handles the detection and tracking of QR Codes
 * and instantiates a GameObject at the position of the QR Code
 */
public class QRCodeManager : MonoBehaviour {

    // The QR Code Watcher object that handles all of the QR Detection and Tracking
    private QRCodeWatcher qRCodeWatcher;

    // The Camera of the Hololens. Needed to transform QR Code position into world space
    [SerializeField]
    private Camera viewerCamera;

    // A Prefab that gets instantiated for each detected qr code
    [SerializeField]
    private GameObject qrTrackerPrefab;

    // A Map containing QRCodeTracker objects for each detected QR Code
    private Dictionary<Guid, QRCodeTracker> qrDictionary;

    // A List of all detected QR Codes
    private List<QRCode> qRCodes = new List<QRCode>();

    async void Start () {

        // Check if the device supports QR Code Tracking
        if (!QRCodeWatcher.IsSupported()) {
            Debug.LogError("QR Code Tracking is not supported");
            gameObject.SetActive(false);
            return;
        }

        // Request Access to the QR Code Watcher
        QRCodeWatcherAccessStatus status = await QRCodeWatcher.RequestAccessAsync();
        Debug.Log(status);

        // Disable the Manager if access has not been given
        if (status != QRCodeWatcherAccessStatus.Allowed) {
            Debug.LogError("QRCodeWatcher access not allowed");
            gameObject.SetActive(false);
            return;
        }

        // Initialize QRCode Prefab Map
        qrDictionary = new Dictionary<Guid, QRCodeTracker>();
        
        // Initialize and start QRCodeWatcher and listen to events
        qRCodeWatcher = new QRCodeWatcher();
        qRCodeWatcher.Added += this.QRAdded;
        qRCodeWatcher.Updated += this.QRUpdated;
        qRCodeWatcher.Removed += this.QRRemoved;
        qRCodeWatcher.Start();
    }

    /**
     * Disable the QRCodeWatcher if this gameobject gets destroyed
     */
    private void OnDestroy() {
        if (qRCodeWatcher != null) qRCodeWatcher.Stop();
        qrDictionary.Clear();
    }

    private void Update() {
        if (qrDictionary == null)
            return;

        // Check if there are new QR Codes, for which there is no gameobject
        foreach (var qr in qRCodes) {
            if (!qrDictionary.ContainsKey(qr.Id)) {
                // If there are new QR Codes, instantiate a new GameObject
                NewCode(qr);
            }
        }

        // Check whether there are Gameobjects for QR Codes that no longer exist
        List<Guid> toRemove = new List<Guid>();
        foreach (var qr in qrDictionary.Keys) {
            if (qRCodes.Find((c) => c.Id == qr) == null) {
                // And destroy those GameObjects
                Destroy(qrDictionary[qr].gameObject);
                toRemove.Add(qr);

                Debug.Log("Removed QR Code with ID: " + qr);
            }
        }

        // Remove QR Codes from the Map that no longer exist
        foreach (var qr in toRemove) {
            qrDictionary.Remove(qr);
        }
    }

    /**
     * Method, which gets called by a button to enable/disable Object Manipulation for EEG Alignment
     */
    public void SetObjectManipulationEnabled(bool enabled) {
        foreach (var tracker in qrDictionary.Values) {
            tracker.gameObject.GetComponentInChildren<ElectrodeInitializer>().SetManipulatorEnabled(enabled);
        }
    }

    /**
     * Method, which gets called by a button to enable/disable the visibility of the reference mesh
     */
    public void SetHeadMeshVisible(bool enabled) {
        foreach (var tracker in qrDictionary.Values) {
            tracker.gameObject.GetComponentInChildren<ElectrodeInitializer>().SetHeadMeshVisible(enabled);
        }
    }

    /**
     * Instantiate a new QRCode GameObject and give it the information about the QR Code
     */
    private void NewCode(QRCode code) {
        GameObject markerObject = Instantiate(qrTrackerPrefab, new Vector3(0, 0, 0), Quaternion.identity);

        // Set the Code and Camera of the Tracker Object
        QRCodeTracker qrTracker = markerObject.GetComponent<QRCodeTracker>();
        qrTracker.SetCode(code, viewerCamera);

        // Set Camera of the Electrode Initializer
        ElectrodeInitializer eInit = markerObject.GetComponentInChildren<ElectrodeInitializer>();
        if (eInit != null) {
            eInit.SetCamera(viewerCamera);
        }

        // Add new QRCode Tracker to Map
        qrDictionary.Add(code.Id, qrTracker);

        Debug.Log("Added new QR Code with value: " + code.Data);
    }

    /**
     * Listener for the Added Event of the QRCodeWatcher
     * It adds the detected QR Code to the list of QR Codes
     */
    private void QRAdded(object sender, QRCodeAddedEventArgs e) {
        if (qRCodes.Find(c => c.Id == e.Code.Id) == null) {
            qRCodes.Add(e.Code);

            Debug.Log("Added new QR Code with value: " + e.Code.Data);
        }
    }

    /**
     * Listener for the Updated Event of the QRCodeWatcher
     * It adds the detected QR Code to the list of QR Codes if it is not in there already
     */
    private void QRUpdated(object sender, QRCodeUpdatedEventArgs e) {
        if (!qrDictionary.ContainsKey(e.Code.Id)) {
            if (qRCodes.Find(c => c.Id == e.Code.Id) == null) {
                qRCodes.Add(e.Code);

                Debug.Log("Added new QR Code with value: " + e.Code.Data);
            }
        }
    }

    /**
     * Listener for the Removed Event of the QRCodeWatcher
     * It removes the detected QR Code from the list of QR Codes
     */
    private void QRRemoved(object sender, QRCodeRemovedEventArgs e) {
        QRCode c = qRCodes.Find(c => c.Id == e.Code.Id);
        if (c != null) {
            qRCodes.Remove(c);

            Debug.Log("Removed QR Code with value: " + e.Code.Data);
        }
    }
}
