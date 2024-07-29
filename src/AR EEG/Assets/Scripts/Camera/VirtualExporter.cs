using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/**
 * Class that takes the Electrodes from the ElectrodeInitializer and outputs the Screen Space coordinates from those electrodes
 * Used for testing OpenCV Codes in python
 */

public class VirtualExporter : MonoBehaviour
{


    public ElectrodeInitializer electrodeInitializer;
    public Camera viewerCamera;


    void Update()
    {
        if (Time.frameCount % 1000 == 0) {
            Matrix4x4 matrix = viewerCamera.projectionMatrix * viewerCamera.worldToCameraMatrix;
            string output = "";

            foreach (var electrode in electrodeInitializer.electrodes) {
                if (!electrode.gameObject.activeSelf)
                    continue;

                Vector3 screenPos = matrix.MultiplyPoint(electrode.transform.position);

                screenPos = new Vector3(screenPos.x + 1f, screenPos.y + 1f, screenPos.z + 1f) / 2f;
                /*screenPos = new Vector3(screenPos.x * Screen.width, screenPos.y * Screen.height, screenPos.z);

                float screenX = screenPos.x / Screen.width;
                float screenY = 1 - (screenPos.y / Screen.height);*/

                screenPos = new Vector3(screenPos.x * viewerCamera.pixelWidth, screenPos.y * viewerCamera.pixelHeight, screenPos.z);

                float screenX = screenPos.x;// / viewerCamera.pixelWidth;
                float screenY = 1 - (screenPos.y);// / viewerCamera.pixelHeight);

                //Debug.Log(electrode.GetComponent<ElectrodeDisplay>().channelName + ": " + screenX + "|" + screenY);

                string xStr = screenX.ToString().Replace(",", ".");
                string yStr = screenY.ToString().Replace(",", ".");

                output += "VirtualElectrode(\"" + electrode.GetComponent<ElectrodeDisplay>().channelName + "\", (" + xStr + "," + yStr + ")),\n";
            }

            Debug.Log(output);
        }
    }
}
