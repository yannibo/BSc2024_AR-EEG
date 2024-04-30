using MixedReality.Toolkit.UX;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ManualAlignmentController : MonoBehaviour {

    // Reference to the Reset Button
    [SerializeField] private PressableButton resetButton;

    /**
     * All references to position, rotation and scale Sliders
     */
    [SerializeField] private Slider posXSlider;
    [SerializeField] private Slider posYSlider;
    [SerializeField] private Slider posZSlider;
    [SerializeField] private Slider rotXSlider;
    [SerializeField] private Slider rotYSlider;
    [SerializeField] private Slider rotZSlider;
    [SerializeField] private Slider sclXSlider;
    [SerializeField] private Slider sclYSlider;
    [SerializeField] private Slider sclZSlider;

    // Offset Vectors for storing Slider Offsets
    Vector3 positionOffset = new Vector3 (0, 0, 0);
    Vector3 rotationOffset = new Vector3(0, 0, 0);
    Vector3 scaleOffset = new Vector3(1, 1, 1);

    /**
     * Start method of Controller registeres Update Events for all Sliders
     */
    void Start() {
        Debug.Log("Registering Slider Listeners");

        resetButton.OnClicked.AddListener(resetClicked);

        posXSlider.OnValueUpdated.AddListener(posXSliderChanged);
        posYSlider.OnValueUpdated.AddListener(posYSliderChanged);
        posZSlider.OnValueUpdated.AddListener(posZSliderChanged);

        rotXSlider.OnValueUpdated.AddListener(rotXSliderChanged);
        rotYSlider.OnValueUpdated.AddListener(rotYSliderChanged);
        rotZSlider.OnValueUpdated.AddListener(rotZSliderChanged);

        sclXSlider.OnValueUpdated.AddListener(sclXSliderChanged);
        sclYSlider.OnValueUpdated.AddListener(sclYSliderChanged);
        sclZSlider.OnValueUpdated.AddListener(sclZSliderChanged);
    }

    void resetClicked() {
        // Reset Slider Values for manual offset
        posXSlider.Value = 0;
        posYSlider.Value = 0;
        posZSlider.Value = 0;
        rotXSlider.Value = 0;
        rotYSlider.Value = 0;
        rotZSlider.Value = 0;
        sclXSlider.Value = 1;
        sclYSlider.Value = 1;
        sclZSlider.Value = 1;

        // Send reset values to the Initializers
        updateCapOffset();

        // Reset Hand Alignment of all Initializers
        ElectrodeInitializer[] allInitializers = FindObjectsOfType<ElectrodeInitializer>();
        foreach (ElectrodeInitializer initializer in allInitializers) {
            initializer.ResetHandAlignment();
        }
    }

    /**
     * All the Update Event Handlers, handling the update of Slider Values
     */
    void posXSliderChanged(SliderEventData eventData) {
        positionOffset.x = eventData.NewValue;
        updateCapOffset();
    }
    void posYSliderChanged(SliderEventData eventData) {
        positionOffset.y = eventData.NewValue;
        updateCapOffset();
    }
    void posZSliderChanged(SliderEventData eventData) {
        positionOffset.z = eventData.NewValue;
        updateCapOffset();
    }

    void rotXSliderChanged(SliderEventData eventData) {
        rotationOffset.x = eventData.NewValue;
        updateCapOffset();
    }
    void rotYSliderChanged(SliderEventData eventData) {
        rotationOffset.y = eventData.NewValue;
        updateCapOffset();
    }
    void rotZSliderChanged(SliderEventData eventData) {
        rotationOffset.z = eventData.NewValue;
        updateCapOffset();
    }

    void sclXSliderChanged(SliderEventData eventData) {
        scaleOffset.x = eventData.NewValue;
        updateCapOffset();
    }
    void sclYSliderChanged(SliderEventData eventData) {
        scaleOffset.y = eventData.NewValue;
        updateCapOffset();
    }
    void sclZSliderChanged(SliderEventData eventData) {
        scaleOffset.z = eventData.NewValue;
        updateCapOffset();
    }

    /**
     * Update the offsets of the EEG caps currently in the scene
     */
    void updateCapOffset() {
        ElectrodeInitializer[] allInitializers = FindObjectsOfType<ElectrodeInitializer>();
        foreach (ElectrodeInitializer initializer in allInitializers) {
            initializer.SetManualOffset(positionOffset, rotationOffset, scaleOffset);
        }
    }
}
