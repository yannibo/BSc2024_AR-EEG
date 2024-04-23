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

    public float samplesPerSecond;

    // A Map storing the indices of channels in the raw data by a channel name
    private Dictionary<string, int> channelIndexMap = new Dictionary<string, int>() {
        { "AF4", 0 },
        { "AF8", 1 },
        { "AFD6h", 2 },
        { "FFC6h", 3 },
        { "F4", 4 },
        { "P3", 5 },
        { "P4", 6 },
        { "Pz", 7 },
        { "O1", 8 },
        { "O2", 9 },
    };

    // A Map containing all registered Instances, which want to receive data from LSL
    private Dictionary<string, List<LSLStreamReceiver>> receivers = new Dictionary<string, List<LSLStreamReceiver>>();

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
        if (client != null) {
            LSLClient.Package pkg = client.ReadChannel("EEG");

            if (pkg.Payload.Length > 0 && pkg.PkgType == LSLClient.FLOAT_TYPE && pkg.ChannelName.Equals("EEG")) {
                samplesPerSecond = 1 / Time.deltaTime;

                float[] values = LSLClient.UnpackFloat(pkg);
                Debug.Log("Received " + values.Length + " values");
                Debug.Log(values);

                foreach (var receiverChannel in receivers.Keys) {
                    if (channelIndexMap.ContainsKey(receiverChannel)) {
                        int index = channelIndexMap[receiverChannel];

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
        Debug.Log("Successfully registered Channel " + label);
    }

    // Unregister a receiver
    public void UnregisterChannelReceiver(string label, LSLStreamReceiver receiever) {
        if (!receivers.ContainsKey(label))
            return;

        receivers[label].Remove(receiever);
    }
}
