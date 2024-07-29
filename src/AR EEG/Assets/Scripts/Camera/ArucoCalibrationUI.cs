using MixedReality.Toolkit.UX;
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/**
 * This class handles the UI for automatic alignment, which contains indicators for all markers and buttons to start calibration and reset it.
 */

public class ArucoCalibrationUI : MonoBehaviour {

    // A reference to the ArucoManager and the ElectrodeInitializer, to get aruco positions and initiate calibration
    public ArucoManager arucoManager;
    public ElectrodeInitializer initializer;

    // Indicators for all 5 aruco markers
    public Toggle frontIndicator;
    public Toggle backIndicator;
    public Toggle leftIndicator;
    public Toggle rightIndicator;
    public Toggle topIndicator;

    // References to the calibrate and reset button
    public PressableButton calibrateButton;
    public PressableButton resetButton;

    void Start() {
        // Disable the calibrate button and hide the reset button
        calibrateButton.enabled = false;
        resetButton.gameObject.SetActive(false);

        // Register for Events about new aruco markers
        arucoManager.MarkerPositionUpdateEvent += this.updatedMarkerPosition;

        // Add listeners for both buttons
        calibrateButton.OnClicked.AddListener(calibrateClicked);
        resetButton.OnClicked.AddListener(resetClicked);
    }

    /**
     * Method that checks indicators for the aruco markers if they are detected
     */
    private void updatedMarkerPosition(ArucoMarker marker) {
        if (marker.id == 1) frontIndicator.isOn = true;
        else if (marker.id == 2) backIndicator.isOn = true;
        else if (marker.id == 3) leftIndicator.isOn = true;
        else if (marker.id == 4) rightIndicator.isOn = true;
        else if (marker.id == 5) topIndicator.isOn = true;

        // In case all markers are detected, enable the calibrate button
        if (
            frontIndicator.isOn &&
            backIndicator.isOn &&
            leftIndicator.isOn &&
            rightIndicator.isOn &&
            topIndicator.isOn
           ) {
            calibrateButton.enabled = true;
        }
    }

    // Initialize the calibration on the ElectrodeInitializer and swap buttons
    private void calibrateClicked() {
        initializer.CalibrateAutomaticPose();

        calibrateButton.gameObject.SetActive(false);
        resetButton.gameObject.SetActive(true);
    }

    // Reset the UI back to before calibration
    private void resetClicked() {
        initializer.ResetAutomaticPose();

        if (
            frontIndicator.isOn &&
            backIndicator.isOn &&
            leftIndicator.isOn &&
            rightIndicator.isOn &&
            topIndicator.isOn
           ) {
            calibrateButton.enabled = true;
        } else {
            calibrateButton.enabled = false;
        }

        calibrateButton.gameObject.SetActive(true);
        resetButton.gameObject.SetActive(false);
    }

}
