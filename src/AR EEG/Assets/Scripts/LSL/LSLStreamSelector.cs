using LSL;
using MixedReality.Toolkit.UX;
using System.Collections.Generic;
using UnityEngine;

/**
 * Was before:
 * Logic behind the LSL Stream Selector, which displays all discovered streams on a ui 
 * and lets the user select one.
 * 
 * Now:
 * Doesn't display available streams because of the incompatability of LSL and ARM64.
 * Is now used to input an IP adress and connect to that directly. (With the Compainoon Script an a PC)
 */
public class LSLStreamSelector : MonoBehaviour {

    // The prefab of a list item of a stream
    /*[SerializeField]
    private GameObject itemPrefab;*/

    // The List UI Element
    [SerializeField]
    private GameObject list;

    // The IP Input Textfield
    [SerializeField]
    private MRTKTMPInputField ipInput;

    // A reference to the connect button
    [SerializeField]
    private PressableButton connectButton;

    // A reference to the disconnect button
    [SerializeField]
    private PressableButton disconnectButton;

    // The UI Element for displaying the selected stream info
    [SerializeField]
    private LSLStreamInfoDisplay infoDisplay;

    // A reference to the LSL Client Script
    [SerializeField]
    private LSLClient lslClient;

    // A map containing all ui list items for each stream
    //private Dictionary<string, LSLStreamItem> items = new Dictionary<string, LSLStreamItem>();

    // a list of all discovered streams
    //private StreamInfo[] streams = new StreamInfo[0];

    void Start()
    {
        // Listen to the events of the LSL Stream Manager about discovered streams
        //LSLStreamManager.instance.streamListUpdated += this.StreamListUpdated;

        connectButton.OnClicked.AddListener(onConnectClick);
        disconnectButton.OnClicked.AddListener(onDisconnectClick);
    }

    /**
     * Update method handling the updates of streams and the ui
     */
    void Update() {
        /*if (LSLStreamManager.instance != null) {
            if (LSLStreamManager.instance.streamStarted) {
                list.SetActive(false);
                infoDisplay.gameObject.SetActive(true);
            } else {
                list.SetActive(true);
                infoDisplay.gameObject.SetActive(false);
            }
        }

        if (streams == null)
            return;

        // Search for streams that have no list item yet and instantiate new list items for those
        foreach (var stream in streams) {
            if (!items.ContainsKey(stream.name())) {
                LSLStreamItem item = Instantiate(itemPrefab, list.transform).GetComponent<LSLStreamItem>();
                item.SetInfo(stream);
                items.Add(stream.name(), item);
            }
        }

        // For each list item check if the stream is still in the discovered array
        // If not remove those list items from the list
        foreach (var item in items.Keys) {
            StreamInfo stream = null;
            foreach (var s in streams) {
                if (s.name() == item) {
                    stream = s;
                    break;
                }
            }

            if (stream == null) {
                Destroy(items[item].gameObject);
                items.Remove(item);
            }
        }*/
    }

    /**
     * Handler for button press of the connect button.
     * Sets Hostname of the LSL CLient and starts it
     */
    void onConnectClick() {
        string ipAddress = ipInput.text;

        Debug.Log("Connecting to: " + ipAddress);

        lslClient._hostName = ipAddress;
        lslClient.enabled = true;

        list.SetActive(false);
        infoDisplay.gameObject.SetActive(true);
    }

    /**
     * Handler for button press of the connect button.
     * Sets Hostname of the LSL CLient and starts it
     */
    void onDisconnectClick() {
        lslClient.StopStream();
        lslClient.enabled = false;

        list.SetActive(true);
        infoDisplay.gameObject.SetActive(false);
    }

    /*private void OnDisable() {
        foreach (var item in items) {
            Destroy(item.Value.gameObject);
        }

        streams = new StreamInfo[0];

        items = new Dictionary<string, LSLStreamItem>();
    }*/

    // Listener for streamListUpdated Event
    /*private void StreamListUpdated(StreamInfo[] obj) {
        streams = obj;
    }*/
}
