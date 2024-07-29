using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using LSL;
using System;

/**
 * Interface for Classes that want to receive LSL Stream Data
 * Currently only contains a method, which is being called with new Data
 * 
 */
public interface LSLStreamReceiver2 {
    void updateData(float data);
}

/**
 * LSL Stream Manager is the main part in regards to the LSL Streams.
 * It handles discovering LSL Streams and the reception of data once a stream has been selected.
 * 
 */
public class LSLStreamManagerNewClient : MonoBehaviour {

    public static LSLStreamManagerNewClient instance;

    // LSL Stream resolver handles discovery of LSL Streams
    private LSLClient client;

    // A number storing the last samples per second
    public float samplesPerSecond;

    // A Map storing the indices of channels in the raw data by a channel name
    private Dictionary<string, int> channelIndexMap = new Dictionary<string, int>() {
        { "FP1", 0 },
        { "FPZ", 1 },
        { "FP2", 2 },
        { "F7", 3 },
        { "F3", 4 },
        { "FZ", 5 },
        { "F4", 6 },
        { "F8", 7 },
        { "FC5", 8 },
        { "FC1", 9 },
        { "FC2", 10 },
        { "FC6", 11 },
        { "M1", 12 },
        { "T7", 13 },
        { "C3", 14 },
        { "CZ", 15 },
        { "C4", 16 },
        { "T8", 17 },
        { "M2", 18 },
        { "CP5", 19 },
        { "CP1", 20 },
        { "CP2", 21 },
        { "CP6", 22 },
        { "P7", 23 },
        { "P3", 24 },
        { "PZ", 25 },
        { "P4", 26 },
        { "P8", 27 },
        { "POZ", 28 },
        { "O1", 29 },
        { "O2", 30 },
        { "HEOGR", 31 },
        { "AF7", 32 },
        { "AF3", 33 },
        { "AF4", 34 },
        { "AF8", 35 },
        { "F5", 36 },
        { "F1", 37 },
        { "F2", 38 },
        { "F6", 39 },
        { "FC3", 40 },
        { "FCZ", 41 },
        { "FC4", 42 },
        { "C5", 43 },
        { "C1", 44 },
        { "C2", 45 },
        { "C6", 46 },
        { "CP3", 47 },
        { "CP4", 48 },
        { "P5", 49 },
        { "P1", 50 },
        { "P2", 51 },
        { "P6", 52 },
        { "HEOGL", 53 },
        { "PO3", 54 },
        { "PO4", 55 },
        { "VEOGU", 56 },
        { "FT7", 57 },
        { "FT8", 58 },
        { "TP7", 59 },
        { "TP8", 60 },
        { "PO7", 61 },
        { "PO8", 62 },
        { "VEOGL", 63 },
    };

    // A Map containing all registered Instances, which want to receive data from LSL
    private Dictionary<string, List<LSLStreamReceiver>> receivers = new Dictionary<string, List<LSLStreamReceiver>>();

    // An Action that gets fired, if the LSL stream is ready
    public event Action streamReady;

    private void OnEnable() {
        // If another instance of the LSL Stream Manager has already been initialized, disable this one
        if (LSLStreamManagerNewClient.instance != null) {
            Debug.LogError("LSLStreamManager already initialized!");
            gameObject.SetActive(false);
            return;
        }

        LSLStreamManagerNewClient.instance = this;
    }

    void Start() {
        // Start the LSL Stream Discovery
        client = GetComponent<LSLClient>();
        if (client == null) {
            Debug.LogError("No LSL Client Component");
            return;
        }

        if (streamReady != null)
            streamReady();
    }

    /**
     * Main Loop of the LSLStreamManager, which handles updating the List of streams when no stream has been selected yet 
     * and updates the channel data if a stream has been selected.
     */
    void Update() {
        if (client != null && !client._noConnection) {
            // Channel is always EEG and is defined in the HoloLSLBridge.py script
            LSLClient.Package pkg = client.ReadChannel("EEG");

            if (pkg.Payload.Length > 0 && pkg.PkgType == LSLClient.FLOAT_TYPE && pkg.ChannelName.Equals("EEG")) {
                samplesPerSecond = 1 / Time.deltaTime;

                float[] values = LSLClient.UnpackFloat(pkg);
                //Debug.Log("Received " + values.Length + " values");
                //Debug.Log(values);

                foreach (var receiverChannel in receivers.Keys) {
                    string uppercaseChannelName = receiverChannel.ToUpperInvariant();

                    if (channelIndexMap.ContainsKey(uppercaseChannelName)) {
                        int index = channelIndexMap[uppercaseChannelName];

                        if (index != -1 && index < values.Length) {
                            foreach (var receiver in receivers[receiverChannel]) {
                                receiver.updateData(values[index]);
                            }
                        }
                    }
                }
            }
        }
    }

    /**
     * Method for receivers to register as a channel. Only receivers that have been registered will receive stream data
     */
    public void RegisterChannelReceiver(string label, LSLStreamReceiver receiver) {
        if (receiver == null)
            return;

        if (!receivers.ContainsKey(label)) {
            receivers[label] = new List<LSLStreamReceiver>();
        }

        receivers[label].Add(receiver);
        //Debug.Log("Successfully registered Channel " + label);
    }

    // Unregister a receiver
    public void UnregisterChannelReceiver(string label, LSLStreamReceiver receiever) {
        if (!receivers.ContainsKey(label))
            return;

        receivers[label].Remove(receiever);
    }
}
