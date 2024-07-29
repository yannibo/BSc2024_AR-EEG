using System;
using TMPro;
using UnityEngine;

/**
 * Script that handles displaying the Stream Info
 */
public class LSLStreamInfoDisplay : MonoBehaviour {

    /**
     * TextMeshPro GameObjects for the respective information
     */

    [SerializeField]
    private TMP_Text streamNameText;

    [SerializeField]
    private TMP_Text streamHostnameText;

    [SerializeField]
    private TMP_Text streamTypeText;

    [SerializeField]
    private TMP_Text streamChannelInfoText;

    [SerializeField]
    private TMP_Text streamManufacturerText;

    [SerializeField]
    private TMP_Text streamSamplesPerSecondText;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {

        /**
         * Initially this was used for the LSL Nuget Package, but this doesn't work on the Hololens, because there is no LSL DLL for Arm64.
         * I still left this code in here, in case someone wants to try it again. The uncommented code is for the approach with the LSLHoloBridge project
         * https://gitlab.csl.uni-bremen.de/fkroll/LSLHoloBridge
         */

        // Set the respective values from streamInfo to the Text Objects
        /*if (LSLStreamManager.instance != null) {
            streamNameText.SetText(LSLStreamManager.instance.streamInfo.name());
            streamHostnameText.SetText(LSLStreamManager.instance.streamInfo.hostname());
            streamTypeText.SetText(LSLStreamManager.instance.streamInfo.type());
            streamChannelInfoText.SetText(LSLStreamManager.instance.streamInfo.channel_count() + " Channels");
            streamManufacturerText.SetText(LSLStreamManager.instance.streamInfo.desc().child("acquisition").child_value("manufacturer"));
            streamSamplesPerSecondText.SetText(Math.Round(LSLStreamManager.instance.samplesPerSecond, 1).ToString() + " Samples/s");
        }*/

        streamNameText.SetText("Holo LSL Bridge");
        streamHostnameText.SetText("-");
        streamTypeText.SetText("EEG");
        streamChannelInfoText.SetText("Unknown Channels");
        streamManufacturerText.SetText("-");
        streamSamplesPerSecondText.SetText(Math.Round(LSLStreamManagerNewClient.instance.samplesPerSecond, 1).ToString() + " Samples/s");
    }

    public void OnStreamCloseClicked() {
        //LSLStreamManager.instance.DeselectStream();
    }
}
