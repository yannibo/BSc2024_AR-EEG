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
public interface LSLStreamReceiver {
    void updateData(float data);
}

/**
 * LSL Stream Manager is the main part in regards to the LSL Streams.
 * It handles discovering LSL Streams and the reception of data once a stream has been selected.
 * 
 */
public class LSLStreamManager : MonoBehaviour {

    public static LSLStreamManager instance;

    // LSL Stream resolver handles discovery of LSL Streams
    private ContinuousResolver resolver;

    // Whether a stream has been selected and is being received
    public bool streamStarted = false;

    // A Countdown for when the script should search for new LSL Streams
    [SerializeField]
    private int streamListUpdateInterval = 5;
    private float nextStreamUpdate = 0;

    // An LSL Inlet, which handles the receiving of data
    private StreamInlet inlet;

    // StreamInfo of the current selected Stream
    public StreamInfo streamInfo;
    public float samplesPerSecond;

    // A Map storing the indices of channels in the raw data by a channel name
    private Dictionary<string, int> channelIndexMap = new Dictionary<string, int>();

    // A local buffer of the last received data and timestamps
    private float[,] data_buffer;
    private double[] timestamp_buffer;

    // A Map containing all registered Instances, which want to receive data from LSL
    private Dictionary<string, List<LSLStreamReceiver>> receivers = new Dictionary<string, List<LSLStreamReceiver>>();

    // Events for listeners for when the list of streams has been updated and when a stream has been selected
    public event Action<StreamInfo[]> streamListUpdated;
    public event Action<StreamInfo> streamReady;
    public event Action<StreamInfo> streamClosed;

    private void OnEnable() {
        // If another instance of the LSL Stream Manager has already been initialized, disable this one
        if (LSLStreamManager.instance != null) {
            Debug.LogError("LSLStreamManager already initialized!");
            gameObject.SetActive(false);
            return;
        }

        LSLStreamManager.instance = this;
    }

    void Start() {
        // Start the LSL Stream Discovery
        resolver = new ContinuousResolver();
    }

    /**
     * Main Loop of the LSLStreamManager, which handles updating the List of streams when no stream has been selected yet 
     * and updates the channel data if a stream has been selected.
     */
    void Update() {
        // If no stream has been selected yet, update the stream list every 5 seconds
        if (!streamStarted) {
            if (nextStreamUpdate <= 0) {
                StartCoroutine(GetRunningStreams());
                nextStreamUpdate = streamListUpdateInterval;
            } else {
                nextStreamUpdate -= Time.deltaTime;
            }

        // If a stream has been selected, receive data and update the registered channels
        } else {
            if (inlet != null) {
                int samples_returned = inlet.pull_chunk(data_buffer, timestamp_buffer);

                if (samples_returned > 0) {
                    Debug.Log("Received " + samples_returned + " Samples for Stream " + inlet.info().name());
                    Debug.Log(receivers.Keys);

                    samplesPerSecond = samples_returned / Time.deltaTime;

                    // Update each receiver based on their channel name
                    foreach (string label in receivers.Keys) {
                        if (receivers[label] == null)
                            continue;

                        int index = channelIndexMap[label];

                        foreach (LSLStreamReceiver receiver in receivers[label]) {
                            Debug.Log("Updating Data for Channel " + label);
                            receiver.updateData(data_buffer[samples_returned - 1, index]);
                        }
                    }

                }
            }
        }
    }

    private void OnDisable() {
        // If a Stream is currently being received, close the Inlet
        if (inlet != null) {
            inlet.Close();
            inlet = null;
        }

        // Close the Resolver
        if (resolver != null) {
            resolver.Close(); 
            resolver = null;
        }

        streamInfo = null;
        samplesPerSecond = 0;

        streamStarted = false;
    }

    // Select the reception of data of a single LSL Stream
    public void SelectStream(string name) {
        if (streamStarted)
            return;

        // Disable the discovery of streams and start the reception of just a single stream
        resolver.Close();
        resolver = new ContinuousResolver("name", name);

        StartCoroutine(StartSelectedStream());
    }

    // Coroutine to handle the stream discovery
    IEnumerator GetRunningStreams() {
        Debug.Log("Getting running Streams...");

        // Wait until results are in from the resolver
        var results = resolver.results();
        while (results.Length == 0) {
            yield return new WaitForSeconds(.1f);
            results = resolver.results();
        }

        Debug.Log("Found " +  results.Length + " Streams");

        // Send event with new list of streams
        if (streamListUpdated != null)
            streamListUpdated(results);
    }

    // Coroutine to initialize the reception of a single stream
    IEnumerator StartSelectedStream() {
        // Wait until the resolver has been initialized and found the stream
        var results = resolver.results();
        while (results.Length == 0) {
            yield return new WaitForSeconds(.1f);
            results = resolver.results();
        }

        // Start the Stream Inlet to receive data
        inlet = new StreamInlet(results[0]);

        // Get Stream Info including the amount and names of the channels
        StreamInfo info = inlet.info();
        streamInfo = info;
        XMLElement chlist = info.desc().child("channels");

        XMLElement ch = chlist.first_child();
        int index = 0;
        while (!ch.empty()) {
            channelIndexMap.Add(ch.child_value("label"), index);
            index++;

            ch = ch.next_sibling();
        }

        // Initialize various buffers
        int buf_samples = (int)Mathf.Ceil((float)(inlet.info().nominal_srate() * 0.2));
        int n_channels = inlet.info().channel_count();

        data_buffer = new float[buf_samples, n_channels];
        timestamp_buffer = new double[buf_samples];

        streamStarted = true;

        // Notify receivers that a stream has been started
        if (streamReady != null) streamReady(info);
    }

    /**
     * Method for receivers to register as a channel. Only receivers that have been registered will receive stream data
     */
    public void RegisterChannelReceiver(string label, LSLStreamReceiver receiver) {
        if (receiver == null)
            return;

        if (inlet == null)
            return;

        if (!channelIndexMap.ContainsKey(label)) {
            Debug.Log("Can't register Channel " + label + ": Doesn't exist in Stream");
            return;
        }

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

    // Stop the reception of stream data and return to discovery of streams
    public void DeselectStream() {
        if (inlet == null)
            return;

        streamStarted = false;

        inlet.Close();
        inlet = null;

        resolver.Close();
        resolver = new ContinuousResolver();

        streamInfo = null;
        samplesPerSecond = 0;

        // Clear channel maps and the registered receivers
        channelIndexMap = new Dictionary<string, int>();
        receivers = new Dictionary<string, List<LSLStreamReceiver>>();
    }
}
