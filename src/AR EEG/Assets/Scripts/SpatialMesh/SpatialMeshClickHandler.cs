using MixedReality.Toolkit.UX;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

public class SpatialMeshClickHandler : MonoBehaviour {

    public GameObject prefab;

    void Start() {
    }

    void Update() {
        
    }

    public void OnPlaceStart(SelectEnterEventArgs args) {
        Instantiate(prefab, args.interactor.attachTransform.position, args.interactor.attachTransform.rotation);
        Debug.Log("On Place Start");
    }

    public void OnPlaceEnd() {
        Debug.Log("On Place End");
    }
}
