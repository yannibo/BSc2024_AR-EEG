using UnityEngine;

/**
 * Class that handles visualizing received channel data
 * incorporates the LSLStreamReceiver interface
 * 
 * Currently takes a mesh and colors it according to the channel data
 */
public class ElectrodeDisplay : MonoBehaviour, LSLStreamReceiver {

    // The Channel Name that this electrode should display
    [SerializeField]
    public string channelName;

    // The Mesh of the electrode in 3d space
    [SerializeField]
    private MeshRenderer m_Renderer;
    
    // The original Position of the electrode used for alignment of the electrode to the head
    public Vector3 originalPosition;

    // Start is called before the first frame update
    void Start()
    {
        // Save the origina position
        originalPosition = transform.position;

        // Listen to the streamReady Event of the LSLStreamManager
        //LSLStreamManager.instance.streamReady += this.LSLStreamReady;
        //LSLStreamManagerNewClient.instance.streamReady += this.LSLStreamReady;
        LSLStreamReady();
    }

    /**
     * When a stream is selected and data of that stream is being received,
     * register this as a receiver with the specified channel name
     */
    //private void LSLStreamReady(LSL.StreamInfo obj) {
    private void LSLStreamReady() {
        Debug.Log("Stream Ready -> Registering Electrode " + channelName);
        //LSLStreamManager.instance.RegisterChannelReceiver(channelName, this);
        LSLStreamManagerNewClient.instance.RegisterChannelReceiver(channelName, this);
    }

    /**
     * Color the specified mesh based on the received data
     */
    public void updateData(float data) {
        Debug.Log("Channel " + channelName + ": " + data);
        m_Renderer.material.color = valueToColor(data);
    }

    // Helper method, which takes a value and returns a color
    private Color valueToColor(float value) {
        if (value < 0.1)
            return Color.red;
        else if (value < 0.2)
            return Color.yellow;
        else
            return Color.green;
    }
}
