using LSL;
using System.Collections.Generic;
using UnityEngine;

/**
 * Logic behind the LSL Stream Selector, which displays all discovered streams on a ui 
 * and lets the user select one.
 */
public class LSLStreamSelector : MonoBehaviour {

    // The prefab of a list item of a stream
    [SerializeField]
    private GameObject itemPrefab;

    // The List UI Element
    [SerializeField]
    private GameObject list;

    // The UI Element for displaying the selected stream info
    [SerializeField]
    private LSLStreamInfoDisplay infoDisplay;

    // A map containing all ui list items for each stream
    private Dictionary<string, LSLStreamItem> items = new Dictionary<string, LSLStreamItem>();

    // a list of all discovered streams
    private StreamInfo[] streams = new StreamInfo[0];
    
    void Start()
    {
        // Listen to the events of the LSL Stream Manager about discovered streams
        //LSLStreamManager.instance.streamListUpdated += this.StreamListUpdated;
    }

    /**
     * Update method handling the updates of streams and the ui
     */
    void Update() {


        list.SetActive(false);
        infoDisplay.gameObject.SetActive(true);

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

    private void OnDisable() {
        foreach (var item in items) {
            Destroy(item.Value.gameObject);
        }

        streams = new StreamInfo[0];

        items = new Dictionary<string, LSLStreamItem>();
    }

    // Listener for streamListUpdated Event
    private void StreamListUpdated(StreamInfo[] obj) {
        streams = obj;
    }
}
